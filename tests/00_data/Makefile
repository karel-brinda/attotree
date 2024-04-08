.PHONY: all help clean cleanall view

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

FASTAS=001334.fa 101058.fa 203692.fa 302649.fa 403790.fa

##############
## Commands ##
##############

all: test_spneumo.tar.xz

test_spneumo.tar.xz: $(FASTAS)
	tar -cvf - $? \
		| xz -T1 -9 \
		> $@.tmp
	mv $@.tmp $@

%.fa:
	curl -L "https://github.com/c2-d2/rase-db-spneumoniae-sparc/raw/master/isolates/$*.fa" \
		| seqtk seq \
		> $@.tmp
	mv $@.tmp $@


help: ## Print help messages
	@echo -e "$$(grep -hE '^\S*(:.*)?##' $(MAKEFILE_LIST) \
		| sed \
			-e 's/:.*##\s*/:/' \
			-e 's/^\(.*\):\(.*\)/   \\x1b[36m\1\\x1b[m:\2/' \
			-e 's/^\([^#]\)/\1/g' \
			-e 's/: /:/g' \
			-e 's/^#\(.*\)#/\\x1b[90m\1\\x1b[m/' \
		| column -c2 -t -s : )"

clean: ## Clean
	rm -fv *.fa

cleanall: clean ## Clean all
	rm -fv *.tar.xz

view: ## View output
