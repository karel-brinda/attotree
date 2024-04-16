.PHONY: all help clean cleanall view

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

G=$(wildcard ~/github/my/rase-db-ngonorrhoeae-gisp/isolates/contigs/*.fa)
$(info $G)


##############
## Commands ##
##############

all: mashtree.nw attotree.nw
	diff $^

attotree.nw:
	../../attotree/attotree.py -t 8 $G > $@.tmp
	mv $@.tmp $@

mashtree.nw:
	mashtree -n 8 $G > $@.tmp
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

cleanall: clean ## Clean all

view: ## View output
