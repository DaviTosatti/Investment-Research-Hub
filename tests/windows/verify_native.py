"""Real Windows smoke test of the shipped bootstrap, processes and persistent database."""

import argparse
import json
import os
import secrets
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from hub_api.cli import create_admin
from hub_api.schemas import MemberCreate
from hub_api.windows_runtime import Runtime, instance_lock


def wait_ready(process, data, previous=None):
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f"Launcher exited before readiness: {process.returncode}")
        path = data / "running.json"
        if path.exists():
            state = json.loads(path.read_text())
            if state["run_id"] != previous:
                with httpx.Client(timeout=3, trust_env=False) as client:
                    try:
                        response = client.get(state["url"] + "/api/v1/health")
                        if response.status_code == 200:
                            return state
                    except httpx.HTTPError:
                        pass
        time.sleep(0.5)
    raise AssertionError("Launcher did not report readiness")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path)
    args = parser.parse_args()
    assert os.name == "nt", "This verification must run on native Windows"
    root, runtime, data = args.root.resolve(), args.runtime_root.resolve(), args.data_root.resolve()
    python = root / ".venv-windows/Scripts/python.exe"
    manager = Runtime(root, runtime, data)
    assert " " in str(root) and any(ord(char) > 127 for char in str(root))
    print("Checking Windows with spaces and Unicode in the installation path.", flush=True)
    with instance_lock(data):
        try:
            manager.start_database()
            manager.migrate()
            for command in [
                [python, "-m", "ruff", "check", "apps/api", "packages/engines", "tests", "scripts/windows/runtime.py"],
                [python, "-m", "mypy"],
                [python, "-m", "pytest", "-q"],
                [python, "-m", "alembic", "check"],
            ]:
                subprocess.run([str(x) for x in command], cwd=root, env=manager.env, check=True)
        finally:
            manager.close()
    npm = runtime / "node/node_modules/npm/bin/npm-cli.js"
    for check in ["test", "typecheck", "lint"]:
        subprocess.run(
            [str(manager.node), str(npm), "run", check], cwd=root / "apps/web", env=manager.env, check=True,
        )
    powershell = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")
    script = root / "scripts/windows/Start-Hub.ps1"
    base = [powershell, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    arguments = ["-RuntimeRoot", str(runtime), "-DataRoot", str(data), "-NoBrowser", "-NonInteractive"]
    log = (data / "native-smoke.log").open("w", encoding="utf-8")
    process = None
    try:
        process = subprocess.Popen(
            base + ["-Action", "Start"] + arguments, cwd=root, env=manager.env,
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
        )
        first = wait_ready(process, data)
        subprocess.run(base + ["-Action", "Check"] + arguments, check=True, env=manager.env)
        password = secrets.token_urlsafe(24)
        create_admin(manager.profile.database_url, MemberCreate(
            email="native@example.com", name="João Windows", password=password, role="admin",
        ))
        with httpx.Client(
            base_url=first["url"], headers={"Origin": first["url"], "X-Hub-Request": "1"},
            timeout=15, trust_env=False,
        ) as client:
            response = client.get("/login")
            assert response.status_code == 200 and 'type="password"' in response.text
            login = client.post("/api/v1/auth/login", json={"email": "native@example.com", "password": password})
            assert login.status_code == 200, login.text
            assert "httponly" in login.headers["set-cookie"].lower()
            owner = client.post("/api/v1/owners", json={"name": "Titular São Paulo"})
            assert owner.status_code == 201, owner.text
            portfolio = client.post("/api/v1/portfolios", json={
                "name": "Carteira Windows", "owner_id": owner.json()["id"], "account_name": "Conta de teste",
            })
            assert portfolio.status_code == 201, portfolio.text
            instrument = client.post("/api/v1/instruments", json={
                "ticker": "WIN3", "name": "Ativo sintético Windows", "asset_class": "stock", "exchange": "TEST",
            })
            assert instrument.status_code == 201, instrument.text
            today = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
            deposit = {"portfolio_id": portfolio.json()["id"], "event_type": "deposit", "gross_amount": "1000", "trade_date": today, "idempotency_key": "windows-deposit-1"}
            event = client.post("/api/v1/transactions", json=deposit)
            assert event.status_code == 201, event.text
            repeated = client.post("/api/v1/transactions", json=deposit)
            assert repeated.status_code in (200, 201) and repeated.json()["id"] == event.json()["id"]
            bought = client.post("/api/v1/transactions", json={
                "portfolio_id": portfolio.json()["id"], "instrument_id": instrument.json()["id"],
                "event_type": "buy", "quantity": "3", "unit_price": "12.34567890", "fees": "0.03",
                "trade_date": today, "idempotency_key": "windows-buy-1",
            })
            assert bought.status_code == 201, bought.text
            quote = client.post("/api/v1/prices", json={"instrument_id": instrument.json()["id"], "price": "12.34", "as_of": today, "source": "Synthetic Windows CI"})
            assert quote.status_code == 201, quote.text
            before = client.get("/api/v1/dashboard", params={"as_of": today}).json()
            from decimal import Decimal

            assert Decimal(before["summary"]["cash"]) == Decimal("962.93")
            assert Decimal(before["summary"]["equity"]) == Decimal("999.95")
            report = client.get("/api/v1/reports/positions.csv", params={"snapshot_id": before["snapshot_id"], "as_of": today})
            assert report.status_code == 200 and "WIN3" in report.text
            assert client.post("/api/v1/auth/logout").status_code == 204
            assert client.get("/api/v1/dashboard").status_code == 401
        # A second launcher must leave the live instance and its data untouched.
        duplicate = subprocess.run(base + ["-Action", "Start"] + arguments, env=manager.env, capture_output=True, timeout=60)
        assert duplicate.returncode != 0
        subprocess.run(base + ["-Action", "Stop"] + arguments, check=True, env=manager.env, timeout=45)
        assert process.wait(timeout=20) == 0
        assert not (data / "running.json").exists()
        assert not manager.database_running()
        assert (data / "profile.json").exists()
        saved_profile = (data / "profile.json").read_bytes()
        process = subprocess.Popen(
            base + ["-Action", "Start"] + arguments, cwd=root, env=manager.env,
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
        )
        second = wait_ready(process, data, first["run_id"])
        assert (data / "profile.json").read_bytes() == saved_profile
        with httpx.Client(
            base_url=second["url"], headers={"Origin": second["url"], "X-Hub-Request": "1"},
            timeout=15, trust_env=False,
        ) as client:
            assert client.post("/api/v1/auth/login", json={"email": "native@example.com", "password": password}).status_code == 200
            after = client.get("/api/v1/dashboard", params={"as_of": today}).json()
            assert after["summary"] == before["summary"]
            assert after["positions"] == before["positions"]
            assert after["snapshot_id"] == before["snapshot_id"]
        # Exercise the distributed CMD wrappers through PowerShell's native argument handling.
        wrapper_env = manager.env | {"HUB_VERIFY_ROOT": str(root), "HUB_VERIFY_RUNTIME": str(runtime), "HUB_VERIFY_DATA": str(data)}
        for wrapper in ["Verificar Hub.cmd", "Parar Hub.cmd"]:
            code = f"& (Join-Path $env:HUB_VERIFY_ROOT '{wrapper}') -RuntimeRoot $env:HUB_VERIFY_RUNTIME -DataRoot $env:HUB_VERIFY_DATA; exit $LASTEXITCODE"
            subprocess.run([powershell, "-NoProfile", "-Command", code], env=wrapper_env, check=True, stdin=subprocess.DEVNULL, timeout=60)
        assert process.wait(timeout=20) == 0
        print("WINDOWS NATIVE PASS: clean install, authentication, exact ledger, CSV, duplicate launch, restart persistence and CMD stop.", flush=True)
    finally:
        if process and process.poll() is None:
            subprocess.run(base + ["-Action", "Stop"] + arguments, env=manager.env, timeout=45)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.terminate()
        log.close()
        # These are controlled CI logs; application credentials are never printed by the launcher.
        if process and process.returncode not in (0, None):
            print((data / "native-smoke.log").read_text(encoding="utf-8", errors="replace")[-18000:])


if __name__ == "__main__":
    main()
