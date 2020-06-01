SHELL=/bin/bash
export PYTHON_VERSION := python3

PYTHON := .venv/bin/python
TWINE := .venv/bin/twine
PIP := .venv/bin/PIP

dist: .venv/bin/python src tests
	@echo "--> Creating distributable"
	$(PYTHON) setup.py sdist bdist_wheel

publish: dist
	@echo "--> Uploading to pypi"
	$(TWINE) upload dist/*


config: setup-venv

setup-venv: .venv/bin/python

.venv/bin/python:
	@rm -rf .venv
	@which virtualenv || sudo easy_install virtualenv
	virtualenv -p $$PYTHON_VERSION .venv
	$(PIP) install -U -r requirements.txt


create-docs: prose-docs api-docs

api-docs:
	@echo creating docs
	pdoc --force --html src/bs_processors

prose-docs:
	$(PIP) install -U -r requirements-doc.txt
	.venv/bin/mkdocs build




upload-docs: create-docs
	# Use this for hotfixing docs, prefer a new release
	$(PIP) install -U ghp-import
	.venv/bin/ghp-import -pf html

doc-server: create-docs
	.venv/bin/mkdocs serve html
.PHONY: docserver

.PHONY: dist publish config setup-venv upload-docs create-docs prose-docs api-docs
