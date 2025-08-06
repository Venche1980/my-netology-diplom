.PHONY: format lint check install

install:
	pip install -r requirements.txt

format:
	@echo "Running isort..."
	isort backend/ netology_pd_diplom/ manage.py
	@echo "Running black..."
	black backend/ netology_pd_diplom/ manage.py
	@echo "Formatting complete!"

lint:
	@echo "Running flake8..."
	flake8 backend/ netology_pd_diplom/ manage.py
	@echo "Linting complete!"

check: format lint
	@echo "All checks passed!"

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete