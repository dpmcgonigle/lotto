# ########################################################################################
#   Lotto
# ########################################################################################

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

PROJECT_NAME=lotto
MAX_LINE_LEN=100
TEST_DIR=test
RELEASE_DIR=dist
TEST_OUTPUT_DIR=reports/tests
COVERAGE_OUTPUT_DIR=reports/coverage

clean: clean-env ## Delete the python virutal env

clean-env:
	if [ -d ./env ]; then rm -Rf ./env; fi
	if [ -d $(TEST_OUTPUT_DIR) ]; then rm -Rf $(TEST_OUTPUT_DIR); fi
	if [ -d $(COVERAGE_OUTPUT_DIR) ]; then rm -Rf $(COVERAGE_OUTPUT_DIR); fi

env: env/.ts ## Create a virtualenv in ./env with all dependencies

# Timestamp file that is only created after './env' has successfully been created via pip install.
#
env/.ts: setup.py Makefile
	python -m venv env
	. ./env/bin/activate
	pip install --upgrade pip
	pip install -e .
	pip install -r test-requirements.txt
	touch env/.ts

format: ## Run all python code through the autopep8 formatter and isort
	black -q $(PROJECT_NAME) $(TEST_DIR)
	autopep8 -vv --in-place --recursive --max-line-length $(MAX_LINE_LEN) --experimental --aggressive $(PROJECT_NAME) $(TEST_DIR)
	autoflake --in-place --remove-all-unused-imports -r $(PROJECT_NAME) $(TEST_DIR)
	isort --verbose --atomic $(PROJECT_NAME) $(TEST_DIR)

.PHONY: build
build: ## Run all python code through Static Analysis
	isort --check $(PROJECT_NAME) $(TEST_DIR)
	autopep8 --exit-code --diff --recursive --max-line-length $(MAX_LINE_LEN) --experimental --aggressive $(PROJECT_NAME) $(TEST_DIR)
	flake8 --verbose $(PROJECT_NAME)/
	mypy --no-implicit-reexport --implicit-reexport --ignore-missing-imports --disallow-incomplete-defs --disallow-untyped-decorators --disallow-incomplete-defs --disallow-untyped-defs --disallow-untyped-decorators --pretty -p $(PROJECT_NAME)

.PHONY: test
test: ## Run all tests.
	pytest -v -o junit_family=xunit1 \
			--junitxml=$(TEST_OUTPUT_DIR)/xml/nosetests.xml \
			--html=$(TEST_OUTPUT_DIR)/html/index.html \
			--cov-report term-missing \
			--cov-fail-under 80.0 \
			--cov=$(PROJECT_NAME) $(TEST_DIR)/ \
			--cov-report xml:$(COVERAGE_OUTPUT_DIR)/xml/coverage.xml

.PHONY: release
release: ## Release the module.
	if [ -d $(RELEASE_DIR) ]; then rm -Rf $(RELEASE_DIR); fi
	python setup.py sdist bdist_wheel -d $(RELEASE_DIR)
