# Makefile for TA-Agent

.PHONY: help install run test docker clean

help:
	@echo "TA-Agent Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make init-db    - Initialize database"
	@echo "  make run        - Run API server (new structure)"
	@echo "  make run-old    - Run API server (old structure)"
	@echo "  make streamlit  - Run Streamlit dashboard"
	@echo "  make test       - Run tests"
	@echo "  make docker     - Start with Docker"
	@echo "  make clean      - Clean cache and logs"

install:
	pip install -r requirements.txt

init-db:
	python scripts/init_db.py

run:
	python -m uvicorn src.api.main_new:app --reload --port 8000

run-old:
	python -m src.api.main

streamlit:
	streamlit run src/dashboard/app.py

test:
	pytest tests/ -v

test-cov:
	pytest --cov=src tests/

docker:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/*/__pycache__
	rm -rf src/*/*/__pycache__
	rm -rf .pytest_cache
	rm -rf logs/*.log
	find . -type d -name "__pycache__" -exec rm -rf {} +
