#!/bin/sh -e
set -x

mypy . && black . --check && isort --check-only . && flake8 .