# compile and execute
.PHONY: clean compile_mods test_gui clean_mods

compile: clean compile_mods clean_mods
# Makefile for compiling mods and running NEURON models


clean:
	rm -rf nmodl/x86_64
	rm -rf hoc/x86_64
	rm -rf python/notebooks/x86_64
	rm -rf $(wildcard hoc/*.mod)
	rm -rf $(wildcard python/notebooks/*.mod)

compile_mods:
	cp $(wildcard nmodl/*.mod) hoc/
	cp $(wildcard nmodl/*.mod) python/notebooks/
	cd hoc/; nrnivmodl $(wildcard *.mod)
	cd python/notebooks/; nrnivmodl $(wildcard *.mod)

clean_mods:
	rm -rf $(wildcard hoc/*.mod)
	rm -rf $(wildcard python/notebooks/*.mod)

test_gui:
	cd hoc;nrngui preliminary_setup_hines_paper.hoc
