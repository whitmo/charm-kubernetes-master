
build: virtualenv lint test

virtualenv:
	virtualenv .venv

lint:
	@.venv/bin/flake8 hooks unit_tests --exclude=charmhelpers
	@.venv/bin/charm proof

test: test-depends
	@CHARM_DIR=. PYTHONPATH=./hooks .venv/bin/py.test unit_tests/*

test-depends: virtualenv
	.venv/bin/pip install -q -r requirements.txt

functional-test:
	@bundletester

clean:
	rm -rf .venv
	find -name *.pyc -delete
