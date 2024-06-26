.PHONY: all all1 all2 help clean cleanall view data

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

FASTAS=$(shell tar -tf test_spneumo.tar.xz)

##########
## Main ##
##########
all: ## Run all tests
all: all1 all2

#w/diff
all1: \
	tree.default.nw \
	tree.default_local_tmp_dir.nw \
	tree.default_verbose_debug.nw \
	tree.file_list.nw \
	tree.file_list_proc_subst.nw \
	tree.file_list_proc_subst_two_lists.nw \
	tree.default_o-param.nw
	for x in $^; do \
		2>&1 echo Testing "$$x"; \
		diff $$x tree.precomputed.newick; \
	done

#w/o diff
all2: \
	tree.default_upgma.nw

data: ## Regenerate test data
data: tree.precomputed.newick file_list.txt


# Different ways to compute trees
tree.default.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py $(shell cat $<) > "$@.tmp"
	mv "$@.tmp" "$@"

tree.default_upgma.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py $(shell cat $<) -m upgma> "$@.tmp"
	mv "$@.tmp" "$@"

tree.default_local_tmp_dir.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py $(shell cat $<) -D -d tmp_dir > "$@.tmp"
	mv "$@.tmp" "$@"

tree.default_o-param.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py $(shell cat $<) -o "$@.tmp"
	mv "$@.tmp" "$@"

tree.default_verbose_debug.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py -V -D $(shell cat $<) > "$@.tmp"
	mv "$@.tmp" "$@"

tree.file_list.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py -L "$<"  > "$@.tmp"
	mv "$@.tmp" "$@"

tree.file_list_proc_subst.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py -L <(head -n 99999 "$<")  > "$@.tmp"
	mv "$@.tmp" "$@"

tree.file_list_proc_subst_two_lists.nw: file_list.txt
	@ >&2 printf "=====\\n$@\\n=====\\n"
	../../attotree/attotree.py -L <(head -n 2 "$<") <(tail -n+3 "$<")  > "$@.tmp"
	mv "$@.tmp" "$@"

tree.precomputed.newick: tree.default.nw
	cp $< $@

file_list.txt: test_spneumo.tar.xz
	tar xvf $<
	tar -tf $< > file_list.txt.tmp
	mv file_list.txt.tmp file_list.txt


###############
## Auxiliary ##
###############
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
	rm -fr tmp_dir/*

cleanall: clean ## Clean all
	rm -f file_list.txt *.fa

view: ## View output
