.PHONY: all help clean cleanall view

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

###################
## Compare trees ##
###################

all: tree.default.nw tree.file_list.nw
	diff $^

###################################
# Different ways to compute trees #
###################################

tree.default.nw: file_list.txt
	cat $< | xargs ../../attotree/attotree.py  > "$@.tmp"
	mv "$@.tmp" "$@"

tree.file_list.nw: file_list.txt
	../../attotree/attotree.py -L "$<"  > "$@.tmp"
	mv "$@.tmp" "$@"

##############
# Input data #
##############

file_list.txt: test_spneumo.tar.xz
	tar xvf $<
	tar -tf $< > $@.tmp
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
	rm -fv *.nw *.fa

cleanall: clean ## Clean all

view: ## View output
