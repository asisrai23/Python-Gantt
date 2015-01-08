# python-gantt Makefile

VERSION=`$(PYTHON) setup.py --version`
ARCHIVE=`$(PYTHON) setup.py --fullname`
PYTHON=python3
PANDOC=~/.cabal/bin/pandoc

install:
	@$(PYTHON) setup.py install

archive: doc readme manifest changelog
	@$(PYTHON) setup.py sdist
	@echo Archive is create and named dist/$(ARCHIVE).tar.gz
	@echo -n md5sum is :
	@md5sum dist/$(ARCHIVE).tar.gz

license:
	@$(PYTHON) setup.py --license

readme:
	@$(PANDOC) -f org -t markdown_github org2gantt/README.org -o org2gantt/README.txt
	@$(PANDOC) -f markdown -t rst README.md -o README.txt

changelog:
	@hg shortlog |~/.cabal/bin/pandoc -f org -t plain > CHANGELOG

manifest: readme changelog
	@$(PYTHON) setup.py sdist --manifest-only

test:
	nosetests gantt
	@(cd org2gantt && $(PYTHON) org2gantt.py  example.org -g test.py && $(PYTHON) test.py && rm test.py)

register:
	@$(PYTHON) setup.py register
	@$(PYTHON) setup.py sdist upload

doc:
	@pydoc3 -w gantt/gantt.py

web: archive
	@cp dist/$(ARCHIVE).tar.gz web/
	@m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/$(ARCHIVE).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm

.PHONY: web
