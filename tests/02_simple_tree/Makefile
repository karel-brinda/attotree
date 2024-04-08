.PHONY: all help clean cleanall view

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

FASTAS=001334.fa 101058.fa 203692.fa 302649.fa 403790.fa

##############
## Commands ##
##############

all: tree.nw tree_file_list.nw

tree.nw: $(FASTAS)
	../../attotree/attotree.py $? > $@.tmp
	mv $@.tmp $@

tree_file_list.nw: $(FASTAS)
	echo "$?" | perl -pe 's/ /\n/g' > file_list.txt
	../../attotree/attotree.py -L file_list.txt  > $@.tmp
	mv $@.tmp $@

%.fa:
	curl -L "https://github.com/c2-d2/rase-db-spneumoniae-sparc/raw/master/isolates/$*" > $@

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
	rm -fv *.nw

cleanall: clean ## Clean all

view: ## View output
