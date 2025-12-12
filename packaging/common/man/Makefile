SOURCES = acm-switchover.1.md acm-switchover-rbac.1.md acm-switchover-state.1.md
TARGETS = $(SOURCES:.md=.1.gz)

all: $(TARGETS)

%.1.gz: %.1.md
	pandoc -s -t man $< -o $(<:.md=.1)
	gzip -f $(<:.md=.1)

clean:
	rm -f *.1 *.1.gz
