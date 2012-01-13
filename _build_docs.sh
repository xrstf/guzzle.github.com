#!/bin/bash

branch=$1
if [ "$branch" = "" ]; then
    branch="master"
fi

if [ ! -d _docs ]; then
    git clone git@github.com:guzzle/guzzle-docs.git _docs && cd _docs && git checkout $branch || exit 1
else
    cd _docs && git pull $branch || exit 2
fi

sed -i '' 's,build/$(LANG),../,g' Makefile
sed -i '' 's,$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html,$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR),g' Makefile
make html