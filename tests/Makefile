TESTS=$(wildcard ??_*/)
.PHONY: all clean $(TESTS)

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

all: $(TESTS)

$(TESTS):
	@echo
	@echo "========================================="
	@echo "$@"
	@echo "========================================="
	@echo
	$(MAKE) -C $@

clean:
	rm -f __*
	@for a in $(TESTS); do \
		$(MAKE) -C $$a clean; \
	done;

