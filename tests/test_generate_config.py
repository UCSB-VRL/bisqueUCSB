import importlib.util
import sys
from pathlib import Path


def load_generator():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "generate-config.py"
    spec = importlib.util.spec_from_file_location("generate_config", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_generator(monkeypatch, tmp_path, **env):
    module = load_generator()
    root = Path(__file__).resolve().parents[1]
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("BISQUE_RUNTIME_DIR", str(runtime))
    monkeypatch.setenv("VENV", str(tmp_path / ".venv"))
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    old_argv = sys.argv
    sys.argv = ["generate-config.py", "--root", str(root)]
    try:
        module.main()
    finally:
        sys.argv = old_argv
    return runtime


def test_generate_config_defaults_to_sqlite(monkeypatch, tmp_path):
    runtime = run_generator(monkeypatch, tmp_path)
    site_cfg = runtime / "config" / "site.cfg"
    test_cfg = runtime / "config" / "test.ini"

    site_text = site_cfg.read_text()
    test_text = test_cfg.read_text()
    h1_text = (runtime / "config" / "h1_paster.cfg").read_text()

    assert "sqlalchemy.url = sqlite:///" in site_text
    assert "bisque.server = http://localhost:8080" in site_text
    assert "host = 0.0.0.0" in h1_text
    assert "use = egg:Paste#http" in h1_text
    assert "protocol_version = HTTP/1.1" in h1_text
    assert f"bisque.paths.data = {runtime / 'data'}" in site_text
    assert "bisque.engine_service.module_dirs = " in site_text
    assert "source/modules" in site_text
    assert "bisque.services_disabled = \n" in site_text
    assert "runtime.platforms = command" in site_text
    assert "bisque.js_environment = development" in site_text
    assert "set debug = true" in site_text
    assert f"results_dir = {runtime / 'data' / 'test-results'}" in test_text


def test_generate_config_maps_postgres_and_smtp_env(monkeypatch, tmp_path):
    dburl = "postgresql://bisque:secret@postgres:5432/bisque"
    runtime = run_generator(
        monkeypatch,
        tmp_path,
        BISQUE_DBURL=dburl,
        BISQUE_SMTP_HOST="smtp.example.test",
        BISQUE_SMTP_PORT="2525",
        BISQUE_SMTP_USER="mailer",
        BISQUE_SMTP_PASSWORD="password",
        BISQUE_MAIL_FROM="bisque@example.test",
    )

    site_text = (runtime / "config" / "site.cfg").read_text()
    test_text = (runtime / "config" / "test.ini").read_text()

    assert f"sqlalchemy.url = {dburl}" in site_text
    assert f"sqlalchemy.url = {dburl}" in test_text
    assert "bisque.smtp.host = smtp.example.test" in site_text
    assert "bisque.smtp.port = 2525" in site_text
    assert "bisque.smtp.username = mailer" in site_text
    assert "bisque.mail.from_email = bisque@example.test" in site_text


def test_generate_config_maps_deployment_debug_env(monkeypatch, tmp_path):
    runtime = run_generator(
        monkeypatch,
        tmp_path,
        BISQUE_DEBUG="false",
        BISQUE_JS_ENVIRONMENT="production",
    )

    site_text = (runtime / "config" / "site.cfg").read_text()

    assert "bisque.js_environment = production" in site_text
    assert "set debug = false" in site_text


def test_generate_config_backs_up_and_preserves_existing_secret(monkeypatch, tmp_path):
    runtime = tmp_path / "runtime"
    config_dir = runtime / "config"
    config_dir.mkdir(parents=True)
    site_cfg = config_dir / "site.cfg"
    site_cfg.write_text("[app:main]\nbeaker.session.secret = keep-me\n")

    runtime = run_generator(monkeypatch, tmp_path)

    site_text = (runtime / "config" / "site.cfg").read_text()
    who_text = (runtime / "config" / "who.ini").read_text()

    assert "beaker.session.secret = keep-me" in site_text
    assert "secret = keep-me" in who_text
    assert (runtime / "config" / "site.cfg.bak").exists()
