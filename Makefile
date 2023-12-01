
tests:
	pytest .

format:
	ruff format --preview .
	isort .
	ruff check --preview --fix .

lint:
	ruff check --preview .
