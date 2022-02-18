set -x

mypy .. && black .. --check && isort --check-only .. && flake8 ..