help:
	@echo analyze    - run the type checker
	@echo check      - run tests
	@echo check-fast - run non-network, non-subprocess tests
	@echo format     - format the code

analyze:
	pipenv run mypy . tests/

check:
	pipenv run pytest

check-fast:
	pipenv run pytest -m "not network and not subprocess"

format:
	pipenv run isort --recursive --use-parentheses --trailing-comma -y -w 80
	pipenv run autoflake -r --in-place --remove-unused-variables .
	pipenv run black -t py38 -l 80 .

format-check:
	pipenv run black -t py38 -l 80 --check .
