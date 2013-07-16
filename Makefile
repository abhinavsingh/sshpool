.PHONY: clean doc audit package release upload text tox

all: clean test

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

doc:
	$(MAKE) -C docs html

audit:
	pep257 sshpool/*.py
	flake8 --ignore=W291,W293,E302 sshpool

package:
	python setup.py sdist

release:
	python setup.py sdist register upload

test:
	nosetests -v --with-coverage --cover-package=sshpool --cover-erase --cover-html --nocapture

tox:
	tox -r