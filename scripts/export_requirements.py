"""Export runtime dependencies from pyproject.toml to requirements.txt."""

import pathlib
import sys
import tomllib


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text())
    deps = data.get("project", {}).get("dependencies", [])
    if deps is None:
        deps = []
    if not isinstance(deps, list):
        raise SystemExit("project.dependencies must be a list")

    output = root / "requirements.txt"
    output.write_text("\n".join(deps) + ("\n" if deps else ""))
    print(f"Wrote {output} with {len(deps)} dependencies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
