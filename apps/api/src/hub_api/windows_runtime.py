"""User-local Windows supervisor. It never installs services or adopts foreign processes."""

import argparse
import contextlib
import ctypes
import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time
import uuid
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import psycopg
from alembic import command
from alembic.config import Config

from hub_api.cli import prompt_first_admin


@dataclass(frozen=True)
class Profile:
    schema_version: int
    database_password: str
    database_port: int = 54329
    api_port: int = 8765
    web_port: int = 8766

    @property
    def database_url(self):
        return f"postgresql+psycopg://hub:{self.database_password}@127.0.0.1:{self.database_port}/hub"

    @property
    def web_url(self):
        return f"http://127.0.0.1:{self.web_port}"


def write_json(path, value):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        os.chmod(temporary, 0o600)
        json.dump(value, stream, ensure_ascii=True, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def load_profile(data, *, create=False):
    path = data / "profile.json"
    if not path.exists():
        if not create:
            raise RuntimeError("Instalacao ainda nao preparada. Execute Iniciar Hub.cmd.")
        if (data / "postgres").exists():
            raise RuntimeError("Banco existente sem profile.json. Restaure a configuracao original.")
        profile = Profile(schema_version=1, database_password=secrets.token_hex(32))
        write_json(path, asdict(profile))
        return profile
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
        profile = Profile(**values)
        ports = (profile.database_port, profile.api_port, profile.web_port)
        valid = (
            profile.schema_version == 1
            and isinstance(profile.database_password, str)
            and len(profile.database_password) == 64
            and all(c in "0123456789abcdef" for c in profile.database_password)
            and all(type(p) is int and 1024 <= p <= 65535 for p in ports)
            and len(set(ports)) == 3
        )
        if not valid:
            raise ValueError
        return profile
    except (ValueError, TypeError) as error:
        raise RuntimeError("profile.json invalido. A configuracao e o banco foram preservados.") from error


@contextlib.contextmanager
def instance_lock(data):
    """An OS lock releases even when a console or process is terminated."""
    path = data / "instance.lock"
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError("O Hub ja esta em execucao ou sendo preparado nesta conta.") from error
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def assert_port_available(port):
    with socket.socket() as candidate:
        if os.name == "nt":
            candidate.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            candidate.bind(("127.0.0.1", port))
        except OSError as error:
            raise RuntimeError(
                f"Porta {port} ocupada. Nenhum processo existente foi encerrado. "
                "Feche a outra execucao ou ajuste as portas em profile.json."
            ) from error


def source_fingerprint(root, api_port):
    """Build identity includes source and the API URL embedded by Next's rewrite."""
    digest = hashlib.sha256(f"windows-build-v1:{api_port}".encode())
    web = root / "apps" / "web"
    paths = list((web / "src").rglob("*"))
    paths += [web / x for x in ("package.json", "package-lock.json", "next.config.ts", "tsconfig.json")]
    manifest = root / "scripts/windows/downloads.json"
    if manifest.exists():
        digest.update(manifest.read_bytes())
    public = web / "public"
    if public.exists():
        paths += list(public.rglob("*"))
    for path in sorted(p for p in paths if p.is_file()):
        digest.update(path.relative_to(web).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


class WindowsJob:
    """Close our child processes if the launcher console disappears unexpectedly."""

    def __init__(self):
        from ctypes import wintypes

        class Limits(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                ("flags", wintypes.DWORD), ("min_working", ctypes.c_size_t),
                ("max_working", ctypes.c_size_t), ("active", wintypes.DWORD),
                ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                ("scheduling", wintypes.DWORD),
            ]

        class Extended(ctypes.Structure):
            _fields_ = [
                ("basic", Limits), ("io", ctypes.c_uint64 * 6),
                ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t),
            ]

        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.handle or not self.kernel.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.close()
            raise RuntimeError("Nao foi possivel supervisionar os processos do Hub no Windows.")

    def add(self, process):
        if not self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)):
            process.terminate()
            process.wait(timeout=10)
            raise RuntimeError("O Windows recusou o grupo de processos do Hub.")

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


class Runtime:
    def __init__(self, root, runtime, data):
        self.root = root.resolve()
        self.runtime = runtime.resolve()
        self.data = data.resolve()
        self.pg = self.runtime / "postgres" / "bin"
        self.node = self.runtime / "node" / "node.exe"
        self.python = self.root / ".venv-windows" / "Scripts" / "python.exe"
        self.cluster = self.data / "postgres"
        self.logs = self.data / "logs"
        self.profile = load_profile(self.data, create=True)
        self.logs.mkdir(exist_ok=True)
        self.env = os.environ.copy()
        self.env.update({
            "HUB_DATABASE_URL": self.profile.database_url,
            "HUB_PUBLIC_ORIGIN": self.profile.web_url,
            "HUB_COOKIE_SECURE": "false",
            "HUB_API_URL": f"http://127.0.0.1:{self.profile.api_port}",
            "NEXT_TELEMETRY_DISABLED": "1",
            "PYTHONUTF8": "1",
            "PGPASSWORD": self.profile.database_password,
            "PATH": str(self.node.parent) + os.pathsep + self.env.get("PATH", ""),
        })
        self.processes = []
        self.log_streams = []
        self.database_started = False
        self.job = None
        # Loopback HTTP must not pass through a corporate or inherited Internet proxy.
        self.http = build_opener(ProxyHandler({}))

    def run(self, args, *, cwd=None, capture=False):
        result = subprocess.run(
            [str(x) for x in args], cwd=cwd or self.root, env=self.env,
            text=True, encoding="utf-8", errors="replace", capture_output=capture,
            creationflags=subprocess.CREATE_NO_WINDOW if capture and os.name == "nt" else 0,
        )
        if result.returncode:
            raise RuntimeError(
                f"Falha em {Path(str(args[0])).name} (codigo {result.returncode}). "
                f"Consulte a mensagem acima e os logs em {self.logs}."
            )
        return result

    def database_running(self):
        return subprocess.run(
            [str(self.pg / "pg_ctl.exe"), "-D", str(self.cluster), "status"],
            env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        ).returncode == 0

    def start_database(self):
        if not (self.cluster / "PG_VERSION").exists():
            if self.cluster.exists():
                raise RuntimeError("Diretorio de banco existente sem PG_VERSION. Nada foi removido.")
            staging = self.data / ("postgres.new-" + uuid.uuid4().hex)
            password_file = self.data / ("initdb-" + uuid.uuid4().hex + ".secret")
            try:
                with password_file.open("x", encoding="ascii") as stream:
                    os.chmod(password_file, 0o600)
                    stream.write(self.profile.database_password + "\n")
                self.run([
                    self.pg / "initdb.exe", "-D", staging, "--username=hub", "--encoding=UTF8",
                    "--locale=C", "--auth=scram-sha-256", f"--pwfile={password_file}",
                ])
                os.replace(staging, self.cluster)
            finally:
                password_file.unlink(missing_ok=True)
                if staging.exists():
                    shutil.rmtree(staging)
        if (self.cluster / "PG_VERSION").read_text().strip() != "17":
            raise RuntimeError("Versao do banco diferente de 17. Migracao automatica nao autorizada.")
        if not self.database_running():
            assert_port_available(self.profile.database_port)
            # pg_ctl can time out after postgres has started. Own cleanup from this point.
            self.database_started = True
            self.run([
                self.pg / "pg_ctl.exe", "-D", self.cluster, "-l", self.logs / "postgres.log",
                "-o", f"-h 127.0.0.1 -p {self.profile.database_port}", "-w", "-t", "60", "start",
            ])
        # This cluster belongs to the dedicated Hub profile, including a previous unclean exit.
        self.database_started = True
        with psycopg.connect(
            host="127.0.0.1", port=self.profile.database_port, user="hub",
            password=self.profile.database_password, dbname="postgres", autocommit=True,
        ) as connection:
            directory = connection.execute("SHOW data_directory").fetchone()[0]
            if os.path.normcase(str(Path(directory).resolve())) != os.path.normcase(str(self.cluster)):
                self.database_started = False
                raise RuntimeError("A porta responde por outro banco. Nenhum servico foi alterado.")
            if not connection.execute("SELECT 1 FROM pg_database WHERE datname = 'hub'").fetchone():
                connection.execute('CREATE DATABASE "hub"')

    def migrate(self):
        config = Config(str(self.root / "alembic.ini"))
        config.set_main_option(
            "script_location", str(self.root / "apps/api/migrations").replace("%", "%%")
        )
        config.set_main_option("sqlalchemy.url", self.profile.database_url.replace("%", "%%"))
        command.upgrade(config, "head")

    def build_web(self):
        web = self.root / "apps" / "web"
        marker = self.root / ".windows-build.json"
        expected = source_fingerprint(self.root, self.profile.api_port)
        old = {}
        if marker.exists():
            with contextlib.suppress(ValueError):
                old = json.loads(marker.read_text())
        if not isinstance(old, dict):
            old = {}
        if old.get("fingerprint") == expected and (web / ".next/BUILD_ID").exists() and (
            web / "node_modules/next/dist/bin/next"
        ).exists():
            print("Interface ja preparada para esta versao.", flush=True)
            return
        npm = self.runtime / "node/node_modules/npm/bin/npm-cli.js"
        print("Preparando a interface Windows (a primeira vez pode levar alguns minutos)...", flush=True)
        self.run([self.node, npm, "ci", "--no-audit", "--no-fund"], cwd=web)
        self.run([self.node, npm, "run", "build"], cwd=web)
        write_json(marker, {"fingerprint": expected})

    def start_process(self, name, args, cwd=None):
        stream = (self.logs / (name + ".log")).open("a", encoding="utf-8")
        self.log_streams.append(stream)
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        process = subprocess.Popen(
            [str(x) for x in args], cwd=cwd or self.root, env=self.env,
            stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
            creationflags=flags if os.name == "nt" else 0,
        )
        self.processes.append(process)
        if self.job:
            self.job.add(process)
        return process

    def wait_url(self, url, *, health=False, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if any(process.poll() is not None for process in self.processes):
                raise RuntimeError(f"Um servico encerrou antes de ficar pronto. Logs: {self.logs}")
            try:
                with self.http.open(url, timeout=3) as response:
                    body = response.read()
                    if response.status == 200 and (
                        not health or json.loads(body).get("database") == "ready"
                    ):
                        return
            except (URLError, TimeoutError, OSError, ValueError):
                pass
            time.sleep(0.3)
        raise RuntimeError(f"Servico nao ficou pronto em {timeout}s. Consulte {self.logs}.")

    def prepare(self, *, interactive):
        print("Iniciando PostgreSQL nativo do Hub...", flush=True)
        self.start_database()
        self.migrate()
        if interactive:
            prompt_first_admin(self.profile.database_url)
        self.build_web()

    def serve(self, *, no_browser):
        assert_port_available(self.profile.api_port)
        assert_port_available(self.profile.web_port)
        self.job = WindowsJob() if os.name == "nt" else None
        self.start_process("api", [
            self.python, "-m", "uvicorn", "hub_api.main:app", "--host", "127.0.0.1",
            "--port", str(self.profile.api_port),
        ])
        self.wait_url(f"http://127.0.0.1:{self.profile.api_port}/api/v1/health", health=True)
        web = self.root / "apps/web"
        self.start_process("web", [
            self.node, web / "node_modules/next/dist/bin/next", "start", "--hostname", "127.0.0.1",
            "--port", str(self.profile.web_port),
        ], cwd=web)
        self.wait_url(self.profile.web_url + "/login")
        self.wait_url(self.profile.web_url + "/api/v1/health", health=True)
        run_id = uuid.uuid4().hex
        stop = self.data / "stop.request.json"
        stop.unlink(missing_ok=True)
        write_json(self.data / "running.json", {
            "run_id": run_id, "url": self.profile.web_url, "pid": os.getpid(),
            "started_at": time.time(), "root": str(self.root),
        })
        print(f"\nHub pronto: {self.profile.web_url}/login", flush=True)
        print("Mantenha esta janela aberta. Para encerrar, use Parar Hub.cmd ou Ctrl+C.", flush=True)
        if not no_browser:
            webbrowser.open(self.profile.web_url + "/login")
        while True:
            if any(process.poll() is not None for process in self.processes):
                raise RuntimeError(f"Um servico encerrou. Consulte os logs em {self.logs}.")
            if stop.exists():
                with contextlib.suppress(ValueError, OSError):
                    if json.loads(stop.read_text()).get("run_id") == run_id:
                        break
            time.sleep(0.5)

    def close(self):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        if self.job:
            self.job.close()
        for stream in self.log_streams:
            stream.close()
        if self.database_started and self.database_running():
            self.run([self.pg / "pg_ctl.exe", "-D", self.cluster, "-m", "fast", "-w", "stop"])
        (self.data / "running.json").unlink(missing_ok=True)
        (self.data / "stop.request.json").unlink(missing_ok=True)


def request_stop(data):
    path = data / "running.json"
    if not path.exists():
        print("Nao ha uma execucao gerenciada ativa.")
        return
    state = json.loads(path.read_text())
    write_json(data / "stop.request.json", {"run_id": state["run_id"]})
    deadline = time.monotonic() + 35
    while path.exists() and time.monotonic() < deadline:
        time.sleep(0.25)
    if path.exists():
        raise RuntimeError("A execucao nao confirmou o encerramento. Confira a janela e os logs do Hub.")
    print("Hub encerrado. Banco e configuracoes preservados.")


def protect_data_directory(data):
    if data.exists() and any(data.iterdir()) and not (data / "profile.json").is_file():
        raise RuntimeError("A pasta de dados nao esta vazia e nao possui perfil do Hub. Escolha uma pasta exclusiva; nenhum arquivo foi alterado.")
    data.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        data.chmod(0o700)
        return
    identity = subprocess.run(
        ["whoami.exe", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    ).stdout
    import re

    sid = re.search(r"S-1-\d+(?:-\d+)+", identity)
    if sid is None:
        raise RuntimeError("Nao foi possivel identificar o usuario Windows para proteger os dados.")
    subprocess.run([
        "icacls.exe", str(data), "/inheritance:r", "/grant:r",
        f"*{sid.group()}:(OI)(CI)F", "*S-1-5-18:(OI)(CI)F", "*S-1-5-32-544:(OI)(CI)F",
    ], stdout=subprocess.DEVNULL, check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Investment Research Hub - Windows nativo")
    parser.add_argument("action", choices=["start", "setup", "stop", "check"])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args(argv)
    if os.name != "nt":
        parser.error("Este inicializador requer Windows 10/11 x64 nativo.")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    data = args.data_root.resolve()
    try:
        if args.action == "stop":
            request_stop(data)
            return 0
        if args.action == "check":
            profile = load_profile(data)
            print(f"Dados: {data}\nInterface: {profile.web_url}/login")
            http = build_opener(ProxyHandler({}))
            with http.open(profile.web_url + "/api/v1/health", timeout=5) as response:
                if response.status != 200 or json.load(response).get("database") != "ready":
                    raise RuntimeError("A verificacao de saude falhou.")
            print("API, interface e PostgreSQL respondem pelo mesmo endereco.")
            return 0
        protect_data_directory(data)
        with instance_lock(data):
            manager = Runtime(args.root, args.runtime_root, data)
            try:
                manager.prepare(interactive=not args.non_interactive)
                if args.action == "start":
                    manager.serve(no_browser=args.no_browser)
            finally:
                manager.close()
    except KeyboardInterrupt:
        print("\nHub encerrado. Dados preservados.")
    except Exception as error:
        # Do not echo arbitrary command lines, SQLAlchemy URLs or secret-bearing payloads.
        message = str(error)
        with contextlib.suppress(Exception):
            message = message.replace(load_profile(data).database_password, "[oculto]")
        print(f"\nNao foi possivel concluir: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
