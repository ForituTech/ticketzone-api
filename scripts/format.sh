autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place events --exclude=__init__.py
black events
isort events

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place payment --exclude=__init__.py
black payments
isort payments

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place tickets --exclude=__init__.py
black tickets
isort tickets

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place partner --exclude=__init__.py
black partner
isort partner