"""Portable helper tests; never invoke the Windows launcher or real Hub services.

Filesystem, lock contention and occupied-port checks are real. PostgreSQL,
Alembic upgrades and npm are replaced only at their external execution boundary.
Windows process/job and HTTP integration remain the native CI's responsibility.
"""

import json
import socket
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from hub_api import windows_runtime as wr


def put(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def snapshot(directory):
    return {
        path.relative_to(directory): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file()
    }


@pytest.fixture
def profile_data():
    return asdict(wr.Profile(schema_version=1, database_password="ab" * 32))


@pytest.fixture
def manager(tmp_path, monkeypatch):
    root = tmp_path / "João da Silva" / "Pesquisa de ações"
    runtime = tmp_path / "Aplicações portáteis"
    data = tmp_path / "Dados preservados"
    for directory in (root, runtime, data):
        directory.mkdir(parents=True)
    put(root / "alembic.ini", "[alembic]\n")
    put(root / "apps/web/src/app/page.tsx", "export default function Page() { return null; }")
    put(root / "apps/web/next.config.ts", "export default {};")
    put(root / "apps/web/package.json", '{"private": true}')
    put(root / "apps/web/package-lock.json", '{"lockfileVersion": 3}')
    put(root / "apps/web/tsconfig.json", "{}")
    put(root / "scripts/windows/downloads.json", '{"schema_version": 1}')
    instance = wr.Runtime(root, runtime, data)
    # A missing mock must fail locally, never start a service or contact a database.
    for name in ("run", "Popen"):
        monkeypatch.setattr(
            wr.subprocess, name, Mock(side_effect=AssertionError("Unexpected process execution"))
        )
    monkeypatch.setattr(
        wr.psycopg, "connect", Mock(side_effect=AssertionError("Unexpected database connection"))
    )
    return instance


def test_profile_is_reused_byte_for_byte_in_unicode_directory(tmp_path):
    data = tmp_path / "João da Silva — finanças"
    data.mkdir()
    first = wr.load_profile(data, create=True)
    before = snapshot(data)
    assert wr.load_profile(data, create=True) == first
    assert wr.load_profile(data) == first
    assert snapshot(data) == before
    assert len(first.database_password) == 64
    assert set(first.database_password) <= set("0123456789abcdef")


@pytest.mark.parametrize("create", [False, True])
@pytest.mark.parametrize(
    "raw",
    [b'{"schema_version":', b"null", b"[]", b'"text"', b"123", b"{}", b"\xff"],
)
def test_corrupt_profile_preserves_credentials_and_cluster(tmp_path, raw, create):
    (tmp_path / "profile.json").write_bytes(raw)
    put(tmp_path / "postgres/PG_VERSION", "17\n")
    put(tmp_path / "postgres/base/portfolio", "irreplaceable synthetic ledger")
    before = snapshot(tmp_path)
    with pytest.raises(RuntimeError, match="profile.json invalido"):
        wr.load_profile(tmp_path, create=create)
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": 2},
        {"database_password": "short"},
        {"database_password": "g" * 64},
        {"database_password": None},
        {"database_port": True},
        {"database_port": "54329"},
        {"api_port": 1023},
        {"web_port": 65536},
        {"web_port": 8765},
        {"unknown_field": "unexpected"},
    ],
)
def test_invalid_profile_fields_do_not_rewrite_file(tmp_path, profile_data, change):
    profile_data.update(change)
    wr.write_json(tmp_path / "profile.json", profile_data)
    before = snapshot(tmp_path)
    with pytest.raises(RuntimeError, match="profile.json invalido"):
        wr.load_profile(tmp_path, create=True)
    assert snapshot(tmp_path) == before


def test_missing_profile_never_generates_new_password_for_existing_cluster(tmp_path):
    put(tmp_path / "postgres/PG_VERSION", "17\n")
    put(tmp_path / "postgres/base/portfolio", "synthetic existing data")
    before = snapshot(tmp_path)
    with pytest.raises(RuntimeError, match="Banco existente sem profile.json"):
        wr.load_profile(tmp_path, create=True)
    assert snapshot(tmp_path) == before


def test_reading_unprepared_profile_is_read_only(tmp_path):
    with pytest.raises(RuntimeError, match="ainda nao preparada"):
        wr.load_profile(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_atomic_json_replace_failure_preserves_original(tmp_path, monkeypatch):
    path = put(tmp_path / "configuração.json", '{"original": true}\n')
    original = path.read_bytes()

    def denied(source, destination):
        assert destination == path
        assert json.loads(source.read_text(encoding="utf-8")) == {"nome": "João"}
        assert path.read_bytes() == original
        raise PermissionError("replacement denied")

    monkeypatch.setattr(wr.os, "replace", denied)
    with pytest.raises(PermissionError, match="replacement denied"):
        wr.write_json(path, {"nome": "João"})
    assert path.read_bytes() == original


def test_instance_lock_excludes_another_process_and_releases_after_exception(tmp_path):
    # Run only the lock helper with this interpreter, never windows_runtime.main.
    code = """
import sys
from pathlib import Path
from hub_api.windows_runtime import instance_lock
try:
    with instance_lock(Path(sys.argv[1])):
        pass
except RuntimeError:
    sys.exit(73)
"""

    def contender():
        result = subprocess.run(
            [sys.executable, "-B", "-c", code, str(tmp_path)],
            capture_output=True, text=True, timeout=20,
        )
        assert result.returncode in (0, 73), result.stderr
        return result.returncode

    with pytest.raises(ValueError, match="interrupted setup"), wr.instance_lock(tmp_path):
        assert contender() == 73
        raise ValueError("interrupted setup")
    assert contender() == 0


def test_port_conflict_does_not_close_existing_listener():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        listener.settimeout(2)
        port = listener.getsockname()[1]
        with pytest.raises(RuntimeError, match=f"Porta {port} ocupada"):
            wr.assert_port_available(port)
        with socket.create_connection(("127.0.0.1", port), timeout=2), listener.accept()[0]:
            assert listener.getsockname()[1] == port


@pytest.mark.parametrize(
    "relative",
    [
        "apps/web/src/app/page.tsx",
        "apps/web/next.config.ts",
        "apps/web/package.json",
        "apps/web/package-lock.json",
        "apps/web/tsconfig.json",
        "apps/web/public/ícone.svg",
        "scripts/windows/downloads.json",
    ],
)
def test_source_fingerprint_detects_build_inputs(manager, relative):
    before = wr.source_fingerprint(manager.root, manager.profile.api_port)
    put(manager.root / relative, "changed build input")
    assert wr.source_fingerprint(manager.root, manager.profile.api_port) != before


def test_source_fingerprint_detects_rewrite_port_rename_and_deletion(manager):
    port = manager.profile.api_port
    original = wr.source_fingerprint(manager.root, port)
    assert wr.source_fingerprint(manager.root, port + 1) != original
    source = manager.root / "apps/web/src/app/page.tsx"
    renamed = source.with_name("layout.tsx")
    source.rename(renamed)
    assert wr.source_fingerprint(manager.root, port) != original
    renamed.rename(source)
    assert wr.source_fingerprint(manager.root, port) == original
    source.unlink()
    assert wr.source_fingerprint(manager.root, port) != original


def test_source_fingerprint_ignores_generated_files_and_checkout_location(manager, tmp_path):
    before = wr.source_fingerprint(manager.root, manager.profile.api_port)
    put(manager.root / "apps/web/.next/generated.js", "generated")
    put(manager.root / "apps/web/node_modules/next/cache.js", "dependency cache")
    put(manager.root / ".windows-build.json", "{}")
    assert wr.source_fingerprint(manager.root, manager.profile.api_port) == before
    relocated = tmp_path / "Outra cópia"
    for relative, content in snapshot(manager.root).items():
        target = relocated / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    assert wr.source_fingerprint(relocated, manager.profile.api_port) == before


def fake_build(manager, monkeypatch):
    def run(args, *, cwd):
        assert cwd == manager.root / "apps/web"
        # Paths containing spaces/Unicode stay whole; no shell or command string.
        assert args[:2] == [
            manager.node, manager.runtime / "node/node_modules/npm/bin/npm-cli.js"
        ]
        if args[2:] == ["ci", "--no-audit", "--no-fund"]:
            put(cwd / "node_modules/next/dist/bin/next", "synthetic next executable")
        else:
            assert args[2:] == ["run", "build"]
            put(cwd / ".next/BUILD_ID", "synthetic build")

    runner = Mock(side_effect=run)
    monkeypatch.setattr(manager, "run", runner)
    return runner


@pytest.mark.parametrize("change", ["source", "api_port", "build_id", "next_executable"])
def test_build_reuses_complete_build_and_rebuilds_when_invalidated(manager, monkeypatch, change):
    runner = fake_build(manager, monkeypatch)
    manager.build_web()
    assert runner.call_count == 2
    manager.build_web()
    assert runner.call_count == 2
    web = manager.root / "apps/web"
    if change == "source":
        put(web / "src/app/page.tsx", "updated application")
    elif change == "api_port":
        manager.profile = replace(manager.profile, api_port=18765)
        manager.env["HUB_API_URL"] = "http://127.0.0.1:18765"
    elif change == "build_id":
        (web / ".next/BUILD_ID").unlink()
    else:
        (web / "node_modules/next/dist/bin/next").unlink()
    manager.build_web()
    assert runner.call_count == 4
    marker = json.loads((manager.root / ".windows-build.json").read_text())
    assert marker["fingerprint"] == wr.source_fingerprint(manager.root, manager.profile.api_port)


def test_failed_build_does_not_publish_success_marker(manager, monkeypatch):
    runner = fake_build(manager, monkeypatch)
    runner.side_effect = [None, RuntimeError("build failed")]
    with pytest.raises(RuntimeError, match="build failed"):
        manager.build_web()
    assert not (manager.root / ".windows-build.json").exists()


@pytest.mark.parametrize("contents", ["{broken", "null", "[]", '"text"', "7"])
def test_corrupt_build_marker_is_rebuilt(manager, monkeypatch, contents):
    runner = fake_build(manager, monkeypatch)
    put(manager.root / ".windows-build.json", contents)
    manager.build_web()
    assert runner.call_count == 2
    assert json.loads((manager.root / ".windows-build.json").read_text())["fingerprint"]


@pytest.mark.parametrize("dirname", ["Pesquisa João da Silva", "Pesquisa 100% João"])
def test_migration_accepts_windows_legal_paths_and_uses_profile_database(
    manager, monkeypatch, dirname
):
    manager.root = manager.root.parent / dirname
    put(manager.root / "alembic.ini", "[alembic]\n")
    upgrade = Mock()
    monkeypatch.setattr(wr.command, "upgrade", upgrade)
    monkeypatch.setenv("HUB_DATABASE_URL", "postgresql+psycopg://unrelated/foreign")
    manager.migrate()
    config, revision = upgrade.call_args.args
    assert revision == "head"
    assert config.get_main_option("script_location") == str(manager.root / "apps/api/migrations")
    assert config.get_main_option("sqlalchemy.url") == manager.profile.database_url


@pytest.mark.parametrize("version", [None, "16\n", "18\n"])
def test_existing_invalid_cluster_is_never_initialized_or_deleted(manager, version):
    put(manager.cluster / "base/portfolio", "synthetic existing data")
    if version is not None:
        put(manager.cluster / "PG_VERSION", version)
    before = snapshot(manager.data)
    with pytest.raises(RuntimeError, match="PG_VERSION|Versao do banco"):
        manager.start_database()
    assert snapshot(manager.data) == before
    assert manager.database_started is False


def test_failed_initdb_removes_only_staging_and_temporary_password(manager, monkeypatch):
    profile = (manager.data / "profile.json").read_bytes()
    backup = put(manager.data / "backups/keep.dump", "synthetic backup")

    def fail_initdb(args):
        assert args[0] == manager.pg / "initdb.exe"
        staging = args[args.index("-D") + 1]
        password_file = Path(next(arg[9:] for arg in args if str(arg).startswith("--pwfile=")))
        assert password_file.read_text().strip() == manager.profile.database_password
        assert all(manager.profile.database_password not in str(arg) for arg in args)
        put(staging / "partial", "partial initialization")
        raise RuntimeError("initdb failed")

    monkeypatch.setattr(manager, "run", fail_initdb)
    with pytest.raises(RuntimeError, match="initdb failed"):
        manager.start_database()
    assert not manager.cluster.exists()
    assert not list(manager.data.glob("postgres.new-*"))
    assert not list(manager.data.glob("*.secret"))
    assert (manager.data / "profile.json").read_bytes() == profile
    assert backup.read_text() == "synthetic backup"


def test_foreign_database_is_not_created_in_or_stopped(manager, monkeypatch, tmp_path):
    put(manager.cluster / "PG_VERSION", "17\n")
    monkeypatch.setattr(manager, "database_running", lambda: True)
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = (str(tmp_path / "foreign cluster"),)
    connect = Mock()
    connect.return_value.__enter__ = Mock(return_value=connection)
    connect.return_value.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(wr.psycopg, "connect", connect)
    runner = Mock()
    monkeypatch.setattr(manager, "run", runner)
    with pytest.raises(RuntimeError, match="outro banco"):
        manager.start_database()
    assert manager.database_started is False
    connection.execute.assert_called_once_with("SHOW data_directory")
    manager.close()
    runner.assert_not_called()


@pytest.mark.parametrize("database_exists", [True, False])
def test_owned_cluster_restart_preserves_profile_and_checks_before_creating_database(
    manager, monkeypatch, database_exists
):
    put(manager.cluster / "PG_VERSION", "17\n")
    put(manager.cluster / "base/portfolio", "synthetic existing ledger")
    before = snapshot(manager.data)
    monkeypatch.setattr(manager, "database_running", lambda: True)
    connection = MagicMock()
    directory_result = Mock()
    directory_result.fetchone.return_value = (str(manager.cluster),)
    database_result = Mock()
    database_result.fetchone.return_value = (1,) if database_exists else None
    connection.execute.side_effect = [directory_result, database_result, Mock()]
    connect = MagicMock()
    connect.return_value.__enter__.return_value = connection
    monkeypatch.setattr(wr.psycopg, "connect", connect)
    runner = Mock()
    monkeypatch.setattr(manager, "run", runner)
    manager.start_database()
    assert manager.database_started is True
    assert connect.call_args.kwargs["port"] == manager.profile.database_port
    sql = [call.args[0] for call in connection.execute.call_args_list]
    assert sql[0] == "SHOW data_directory"
    assert ('CREATE DATABASE "hub"' in sql) is not database_exists
    runner.assert_not_called()
    manager.close()
    runner.assert_called_once()
    assert runner.call_args.args[0] == [
        manager.pg / "pg_ctl.exe", "-D", manager.cluster, "-m", "fast", "-w", "stop"
    ]
    assert snapshot(manager.data) == before


def test_migration_failure_prevents_build_and_first_admin_prompt(manager, monkeypatch):
    start = Mock()
    monkeypatch.setattr(manager, "start_database", start)
    monkeypatch.setattr(manager, "migrate", Mock(side_effect=RuntimeError("migration failed")))
    build = Mock()
    admin = Mock()
    monkeypatch.setattr(manager, "build_web", build)
    monkeypatch.setattr(wr, "prompt_first_admin", admin)
    with pytest.raises(RuntimeError, match="migration failed"):
        manager.prepare(interactive=True)
    start.assert_called_once()
    build.assert_not_called()
    admin.assert_not_called()


def test_pg_ctl_start_timeout_does_not_leave_owned_database_running(manager, monkeypatch):
    """pg_ctl -w can time out while its independently spawned server stays alive."""
    put(manager.cluster / "PG_VERSION", "17\n")
    put(manager.cluster / "base/portfolio", "synthetic existing ledger")
    before = snapshot(manager.data)
    server = {"running": False}
    monkeypatch.setattr(manager, "database_running", lambda: server["running"])
    monkeypatch.setattr(wr, "assert_port_available", Mock())

    def run(args):
        assert args[0] == manager.pg / "pg_ctl.exe"
        assert args[args.index("-D") + 1] == manager.cluster
        if args[-1] == "start":
            server["running"] = True
            raise RuntimeError("server did not start in time")
        assert args[-1] == "stop"
        server["running"] = False

    monkeypatch.setattr(manager, "run", run)
    with pytest.raises(RuntimeError, match="did not start in time"):
        manager.start_database()
    manager.close()
    assert server["running"] is False
    assert snapshot(manager.data) == before
