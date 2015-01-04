# python-gantt Makefile

VERSION=`python3 setup.py --version`
ARCHIVE=`python3 setup.py --fullname`

readme:
	@~/.cabal/bin/pandoc -f org -t markdown_github README.org -o README.txt

changelog:
	@hg shortlog |~/.cabal/bin/pandoc -f org -t plain > CHANGELOG

manifest: readme changelog
	@python3 setup.py sdist --manifest-only

test:
	@(cd gantt; python3 gantt.py)
	@python3 org2gantt.py  example.org -g test.py
	@python3 test.py
	@rm test.py

install:
	@python3 setup.py install

archive: doc readme
	@python3 setup.py sdist
	@echo Archive is create and named dist/$(ARCHIVE).tar.gz
	@echo -n md5sum is :
	@md5sum dist/$(ARCHIVE).tar.gz

license:
	@python3 setup.py --license

register:
	@python3 setup.py register
	@python3 setup.py sdist upload

doc:
	@pydoc3 -w gantt/gantt.py
#	@cd docs && make html

#web:
#	@cp dist/$(ARCHIVE).tar.gz web/
#	@m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/$(ARCHIVE).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm

.PHONY: web
