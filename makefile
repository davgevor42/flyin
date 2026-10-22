PYTHON = python3

install:
	$(PYTHON) -m pip install flake8 mypy

run:
ifndef MAP
	$(error MAP is not set. Usage: make run MAP=path/to/map.txt)
endif
	$(PYTHON) main.py $(MAP)

debug: check-map
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict