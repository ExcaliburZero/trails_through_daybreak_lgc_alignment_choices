.PHONY: lint

lint:
	python -m black ttdlgc
	python -m mypy ttdlgc
	python -m ruff check ttdlgc
