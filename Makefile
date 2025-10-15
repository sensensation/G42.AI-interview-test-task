# Running
start:
	docker-compose up --build -d

stop:
	docker-compose down

# Linting
format:
	uv run ruff format .

lint:
	uv run ruff format --check .
	uv run ruff check .


# Testing
test:
	uv run pytest .

check: format lint test
