SOURCES = acm-switchover.1.md acm-switchover-rbac.1.md acm-switchover-state.1.md
TARGETS = $(SOURCES:.1.md=.1.gz)

all: $(TARGETS)

%.1.gz: %.1.md
	@command -v pandoc >/dev/null 2>&1 || { echo "pandoc is required to build man pages"; exit 127; }
	pandoc -s -t man $< -o $(@:.gz=)
	gzip -f $(@:.gz=)

clean:
	rm -f *.1 *.1.gz
