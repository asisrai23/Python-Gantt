# python-gantt Makefile

VERSION=`python setup.py --version`
ARCHIVE=`python setup.py --fullname`

manifest:
        @python setup.py sdist --manifest-only

test:
        @(cd gantt; python3 gantt.py)

install:
        @python3 setup.py install

archive: doc
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
        @cd docs && make html

#web:
#        @cp dist/$(ARCHIVE).tar.gz web/
#        @m4 -DVERSION=$(VERSION) -DMD5SUM=$(shell md5sum dist/$(ARCHIVE).tar.gz |cut -d' ' -f1) -DDATE=$(shell date +%Y-%m-%d) web/index.gtm.m4 > web/index.gtm

.PHONY: web
