import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_command(command: list[str], cwd: Path) -> None:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise RuntimeError(f"{' '.join(command)} :: {stderr}")


def resolve_agent_browser() -> str:
    for candidate in ("agent-browser.cmd", "agent-browser", "agent-browser.ps1"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError("agent-browser executable was not found in PATH")


def run_agent_browser(case_dir: Path, viewport_height: int, executable: str) -> None:
    html_path = case_dir / "card.html"
    png_path = case_dir / "card.png"
    file_url = html_path.resolve().as_uri()
    session = f"card-creator-{case_dir.name}"

    commands = [
        [
            executable,
            "--session",
            session,
            "--allow-file-access",
            "open",
            file_url,
        ],
        [executable, "--session", session, "wait", "--load", "networkidle"],
        [
            executable,
            "--session",
            session,
            "set",
            "viewport",
            "1080",
            str(viewport_height),
            "2",
        ],
        [
            executable,
            "--session",
            session,
            "screenshot",
            "--full",
            str(png_path),
        ],
        [executable, "--session", session, "close"],
    ]

    try:
        for command in commands:
            run_command(command, case_dir)
    finally:
        subprocess.run(
            [executable, "--session", session, "close"],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )


def build_png_validation_command(script_dir: Path, case_dir: Path, png_validation: dict[str, Any]) -> list[str]:
    return [
        sys.executable,
        str(script_dir / "validate_png.py"),
        str(case_dir / "card.png"),
        "--expected-width",
        str(png_validation["expected_width"]),
        "--min-height",
        str(png_validation["min_height"]),
        "--min-ratio",
        str(png_validation["min_ratio"]),
        "--reject-blank",
    ]


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_matches(name: str, selected: set[str] | None) -> bool:
    return selected is None or name in selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        action="append",
        dest="cases",
        help="Only run selected case names from manual-runs/manifest.json",
    )
    parser.add_argument(
        "--recapture",
        action="store_true",
        help="Rebuild card.png from card.html using agent-browser before validating it",
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=1200,
        help="Initial viewport height used when --recapture is enabled",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent
    manual_runs_dir = skill_root / "manual-runs"
    manifest = load_manifest(manual_runs_dir / "manifest.json")
    selected_cases = set(args.cases) if args.cases else None
    agent_browser = resolve_agent_browser() if args.recapture else ""

    failures: list[str] = []
    ran_any_case = False

    for case in manifest["cases"]:
        name = case["name"]
        if not case_matches(name, selected_cases):
            continue
        ran_any_case = True
        case_dir = manual_runs_dir / case["dir"]
        print(f"[case:{name}] start")

        try:
            run_command(
                [
                    sys.executable,
                    str(script_dir / "validate_design_json.py"),
                    str(case_dir / "design.json"),
                ],
                skill_root,
            )
            print(f"[case:{name}] design.json ok")

            run_command(
                [
                    sys.executable,
                    str(script_dir / "validate_html.py"),
                    str(case_dir / "card.html"),
                ],
                skill_root,
            )
            print(f"[case:{name}] card.html ok")

            png_validation = case["png_validation"]
            png_command = build_png_validation_command(script_dir, case_dir, png_validation)

            if args.recapture:
                last_error: RuntimeError | None = None
                for attempt in range(1, 3):
                    run_agent_browser(case_dir, args.viewport_height, agent_browser)
                    print(f"[case:{name}] card.png recaptured (attempt {attempt})")
                    try:
                        run_command(png_command, skill_root)
                        last_error = None
                        break
                    except RuntimeError as exc:
                        last_error = exc
                        if attempt == 2:
                            raise
                        print(f"[case:{name}] blank or invalid screenshot detected, retrying")
                if last_error is not None:
                    raise last_error
            else:
                run_command(png_command, skill_root)

            print(f"[case:{name}] card.png ok")
        except RuntimeError as exc:
            failures.append(f"{name}: {exc}")
            print(f"[case:{name}] FAIL")

    if not ran_any_case:
        print("ERROR: no matching cases found", file=sys.stderr)
        return 1

    if failures:
        print("\nRegression failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nRegression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
