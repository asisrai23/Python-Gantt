# python-gantt Makefile

VERSION=`$(PYTHON) setup.py --version`
ARCHIVE=`$(PYTHON) setup.py --fullname`
PYTHON=python3


readme:
	@~/.cabal/bin/pandoc -f org -t markdown_github README.org -o README.txt

changelog:
	@hg log --style changelog | sed 's/@/ at /g'> CHANGELOG

manifest: readme changelog
	@$(PYTHON) setup.py sdist --manifest-only

test:
	@(cd gantt; $(PYTHON) gantt.py)
	@$(PYTHON) org2gantt.py  example.org -g test.py
	@$(PYTHON) test.py
	@rm test.py

install:
	@$(PYTHON) setup.py install

archive: doc readme
	@$(PYTHON) setup.py sdist
	@echo Archive is create and named dist/$(ARCHIVE).tar.gz
	@echo -n md5sum is :
	@md5sum dist/$(ARCHIVE).tar.gz

license:
	@$(PYTHON) setup.py --license

register:
	@$(PYTHON) setup.py register
	@$(PYTHON) setup.py sdist upload

doc:
	@pydoc3 -w gantt/gantt.py
#	@cd docs && make html

#web:
#	@cp dist/$(ARCHIVE).tar.gz web/
#	@m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/$(ARCHIVE).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm

.PHONY: web
