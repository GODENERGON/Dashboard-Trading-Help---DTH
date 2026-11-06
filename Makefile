VENV ?= .venv
PY := $(VENV)/bin/python
BACKEND := backend

.PHONY: install lint format test check api backtest clean

$(PY):
	python3 -m venv $(VENV)

install: $(PY)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e "$(BACKEND)[dev,data]"

lint:
	$(PY) -m ruff check $(BACKEND)
	$(PY) -m ruff format --check $(BACKEND)

format:
	$(PY) -m ruff format $(BACKEND)
	$(PY) -m ruff check --fix $(BACKEND)

test:
	cd $(BACKEND) && ../$(PY) -m pytest

check: lint test

api:
	$(PY) -m uvicorn dth.api.main:app --reload --host 127.0.0.1 --port 8765

backtest:
	$(PY) -m dth.cli backtest-demo

clean:
	rm -rf $(VENV) .pytest_cache $(BACKEND)/.pytest_cache .ruff_cache
