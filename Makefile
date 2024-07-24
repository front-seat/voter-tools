.PHONY: check test build install-dev

check:
	ruff format --check
	ruff check
	mypy .
	python -m unittest

test:
	python -m unittest

build:
	# Requires setuptools, wheel, and build deps
	python -m build

install-dev:
	pip install '.[dev]'

