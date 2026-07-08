set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments := true
set dotenv-load := false

default:
    just --list

help:
    just --list

bootstrap *args:
    scripts/bootstrap-uv.sh --dev "$@"

_setup-runtime: bootstrap
    scripts/setup-bisque-local.sh

doctor *args:
    scripts/doctor.sh "$@"

setup: _setup-runtime

up *args: _setup-runtime
    scripts/start-bisque-local.sh --force "$@"

run *args:
    scripts/start-bisque-local.sh "$@"

restart *args:
    scripts/start-bisque-local.sh --force "$@"

stop *args:
    scripts/stop-bisque-local.sh "$@"

docker-build *args:
    scripts/docker-build.sh "$@"

docker-run *args:
    scripts/docker-run-local.sh "$@"

test *args:
    scripts/test-smoke.sh "$@"

test-unit *args:
    scripts/test-unit.sh "$@"

test-services *args:
    scripts/test-services.sh "$@"

test-live *args:
    scripts/test-smoke.sh --live "$@"

clean-runtime:
    scripts/clean-runtime.sh
