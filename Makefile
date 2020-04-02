# compile and execute

all: clean compile_mods test_gui

.PHONY: all clean compile_mods test_gui

clean:
	rm -rf nmodl/x86_64
	rm -rf hoc/x86_64
	rm -rf $(wildcard hoc/*.mod)

compile_mods:
	cp $(wildcard nmodl/*.mod) hoc/
	cd hoc/; nrnivmodl $(wildcard *.mod)
	rm -rf $(wildcard hoc/*.mod)

test_gui:
	cd hoc;nrngui preliminary_setup_hines_paper.hoc
