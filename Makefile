
tests:
	pytest .

fast-tests:
	pytest . -m 'not slow'

format:
	ruff format --preview .
	isort .
	ruff check --preview --fix .

lint:
	ruff check --preview .
