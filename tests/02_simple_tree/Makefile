.PHONY: all help clean cleanall view

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

FASTAS=$(shell tar -tf test_spneumo.tar.xz)

###################
## Compare trees ##
###################

all: tree.precomputed.newick tree.default.nw tree.file_list.nw
	for x in $^; do \
		2>&1 echo Testing "$$x"; \
		diff $$x tree.precomputed.newick; \
	done

###################################
# Different ways to compute trees #
###################################

tree.default.nw: file_list.txt
	../../attotree/attotree.py $(shell cat $<) > "$@.tmp"
	mv "$@.tmp" "$@"

tree.file_list.nw: file_list.txt
	../../attotree/attotree.py -L "$<"  > "$@.tmp"
	mv "$@.tmp" "$@"

tree.precomputed.newick: tree.default.nw
	cp $< $@

##############
# Input data #
##############

file_list.txt: test_spneumo.tar.xz
	tar xvf $<
	tar -tf $< > file_list.txt.tmp
	mv file_list.txt.tmp file_list.txt

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
	rm -f *.nw *.tmp

cleanall: clean ## Clean all
	rm -f file_list.txt *.fa

view: ## View output
