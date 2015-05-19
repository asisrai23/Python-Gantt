# python-gantt Makefile

VERSION=`$(PYTHON) setup.py --version`
ARCHIVE=`$(PYTHON) setup.py --fullname`
PYTHON=python3.2
PANDOC=~/.cabal/bin/pandoc

install:
	@$(PYTHON) setup.py install

archive: doc readme changelog
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


test:
	nosetests gantt

	$(PYTHON) org2gantt/org2gantt.py  org2gantt/example.org -r -g test.py 
	$(PYTHON) test.py
	rm test.py

conformity:
	pyflakes org2gantt/org2gantt.py
	pyflakes gantt/gantt.py
	flake8 org2gantt/org2gantt.py
	flake8 gantt/gantt.py


pipregister:
	python2.7 setup.py register

register: test
	python2.7 setup.py sdist upload --identity="Alexandre Norman" --sign --quiet

doc:
	@pydoc -w gantt/gantt.py

web:	test
	cp dist/$(ARCHIVE).tar.gz web/
	m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/$(ARCHIVE).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm
	(cd web_upper ; make all)
	convert project.svg web/project.png 
	convert project_resources.svg web/project_resources.png 
	optipng web/project.png
	optipng web/project_resources.png
	echo "put project.png;put project_resources.png;put index.*;put $(ARCHIVE).tar.gz"| (cd web ; ncftp python-gantt)

.PHONY: web
