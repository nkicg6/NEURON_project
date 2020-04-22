# compile and execute

all: clean compile_mods test_gui
# Makefile for compiling mods and running NEURON models
.PHONY: all clean compile_mods test_gui

clean:
	rm -rf nmodl/x86_64
	rm -rf hoc/x86_64
	rm -rf $(wildcard hoc/*.mod)

compile_mods:
	cp $(wildcard nmodl/*.mod) hoc/
	cd hoc/; nrnivmodl $(wildcard *.mod)
	rm -rf $(wildcard hoc/*.mod)
# testing python use
	cp $(wildcard nmodl/*.mod) python/notebooks/
	cd python/notebooks/; nrnivmodl $(wildcard *.mod)
	rm -rf $(wildcard pyhont/notebooks/*.mod)


test_gui:
	cd hoc;nrngui preliminary_setup_hines_paper.hoc
