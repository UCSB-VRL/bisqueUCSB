import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_runtime_env(dotenv: Path, **env):
    process_env = {
        "PATH": os.environ["PATH"],
        "BISQUE_DOTENV": str(dotenv),
        **env,
    }
    result = subprocess.run(
        [
            "bash",
            "-lc",
            "source scripts/runtime-env.sh; "
            "printf '%s\n' "
            '"$BISQUE_PUBLIC_URL" '
            '"$BISQUE_HTTP_PORT" '
            '"$BISQUE_ORGANIZATION" '
            '"$BISQUE_SMTP_USER" '
            '"$BISQUE_RUNTIME_DIR"',
        ],
        cwd=ROOT,
        env=process_env,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.splitlines()


def test_runtime_env_loads_dotenv_defaults(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "\n".join(
            [
                "# comments and blank lines are ignored",
                "BISQUE_PUBLIC_URL=http://localhost:27000",
                "BISQUE_HTTP_PORT=27000",
                "export BISQUE_ORGANIZATION='Example Org'",
                "BISQUE_SMTP_USER=",
                "",
            ]
        )
    )

    values = run_runtime_env(dotenv)

    assert values[0] == "http://localhost:27000"
    assert values[1] == "27000"
    assert values[2] == "Example Org"
    assert values[3] == ""
    assert values[4] == str(ROOT / ".bisque")


def test_runtime_env_keeps_exported_env_over_dotenv(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "\n".join(
            [
                "BISQUE_PUBLIC_URL=http://localhost:27000",
                "BISQUE_HTTP_PORT=27000",
            ]
        )
    )

    values = run_runtime_env(
        dotenv,
        BISQUE_PUBLIC_URL="http://localhost:8088",
    )

    assert values[0] == "http://localhost:8088"
    assert values[1] == "27000"
