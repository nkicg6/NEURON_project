import sys
sys.path.insert(0,"mitral_cell")
from pprint import pprint
from neuron import h
from mitralcell import MitralCell

h.nrn_load_dll("../nmodl/x86_64/.libs/libnrnmech.so")

if __name__ == "__main__":
    cell = MitralCell("1", nodes=5)

    for sec in h.allsec():
        pprint(h.psection(sec))
    print("Exited normally")
    sys.exit(1)
