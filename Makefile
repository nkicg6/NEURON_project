# Makefile for compiling mods and running NEURON models
.PHONY: clean compile_mods compile

compile: clean compile_mods

clean:
	rm -rf nmodl/x86_64
compile_mods:
	cd nmodl/; nrnivmodl $(wildcard *.mod)
