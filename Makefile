compose_cmd = docker-compose -f docker/docker-compose.yml

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"


# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXBUILD = sphinx-build
SOURCEDIR = docs
BUILDDIR = docs/_build


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
build_doc:
	rm -rf docs/_build/*
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)"


run_doc:
	rm -rf docs/_build/*
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)"
	$(BROWSER) docs/_build/index.html


develop:
	pip install ".[dev]"
	pre-commit install

# DB

start_db:
	$(compose_cmd) up -d scrud_db

stop_db:
	$(compose_cmd) down

# DJANGO

makemigrations:
	python manage.py makemigrations scrud_django


migrate:
	python manage.py migrate scrud_django


run_tests:
	# Note: for now, run tests for each module because the follow error:
	# AttributeError: The step `get` couldn't be found for the prefix type `Http`
	pytest -vv tests/test_models.py
	pytest -vv tests/test_rest.py

# LINTER AND CODE CHECKING
pre_commit_check:
	pre-commit run --all-files
