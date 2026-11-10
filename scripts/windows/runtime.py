"""Entry point used by the native PowerShell bootstrap."""
from hub_api.windows_runtime import main

if __name__ == "__main__":
    raise SystemExit(main())
