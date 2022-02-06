set -x

black .. --check && isort --check-only .. && flake8 ..