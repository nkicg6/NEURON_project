import numpy as np
from neuron import h
from neuron.units import ms
from neuron.units import mV as mv


h.load_file("stdrun.hoc")
h.nrn_load_dll("../../hoc")

class MitralCell:
    def __init__(self, uid, nodes):
        self._uid = uid
        self.stim_what = ""
        self.stim_dict = {}
        self.celsius = 23
        self.n_myelinated_segs = nodes + 1
        self.n_nodes = nodes
        self.nodes_list = []
        self.myelinated_segs_list = []
        self.node_length = 1.5
        self.myelinated_segment_length = 200
        self.myelin_diameter = 4
        self.myelin_nseg = 15
        self.node_nseg = 3
        self.node_diameter = 1
        self.ais_length = 30
        self.experiment_temperature = 36
        h.celsius = self.experiment_temperature
        self._define_morphology()
        self._setup_morphology()
        self._setup_biophysics()

    def _make_ais(self):
        self.proximal_ais = h.Section(name="proximal_ais", cell=self)
        self.distal_ais = h.Section(name="distal_ais", cell=self)

    def _make_myelinated_segments(self):
        for n in range(self.n_myelinated_segs):
            self.myelinated_segs_list.append(
                h.Section(name=f"myelin_seg_{n}", cell=self)
            )

    def _make_nodes(self):
        for n in range(self.n_nodes):
            self.nodes_list.append(h.Section(name=f"node_{n}", cell=self))

    def _define_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dend = h.Section(name="dend", cell=self)
        self._make_ais()
        self._make_myelinated_segments()
        self._make_nodes()
        self.active = [self.soma, self.proximal_ais, self.distal_ais, *self.nodes_list]
        self.passive = [self.dend, *self.myelinated_segs_list]
        self.all_segs = self.active + self.passive

    def _setup_morphology(self):
        self.dend.connect(self.soma, 0, 1)
        self.proximal_ais.connect(self.soma, 1)
        self.distal_ais.connect(self.proximal_ais, 1)
        self.myelinated_segs_list[0].connect(self.distal_ais, 1)
        # connect all myelinated segments and nodes
        for n, _ in enumerate(self.myelinated_segs_list):
            try:
                self.nodes_list[n].connect(self.myelinated_segs_list[n], 1)
                self.myelinated_segs_list[n + 1].connect(self.nodes_list[n], 1)
            except:
                print("Connections done")
                pass
        for myelin, node in zip(self.myelinated_segs_list, self.nodes_list):
            node.L = self.node_length
            node.diam = self.node_diameter
            node.nseg = self.node_nseg
            myelin.L = self.myelinated_segment_length
            myelin.diam = self.myelin_diameter
            myelin.nseg = self.myelin_nseg
        self.soma.L = 20
        self.soma.diam = 20
        self.soma.nseg = 3
        self.dend.L = 200
        self.dend.diam = 5
        self.dend.nseg = 15
        self.proximal_ais.L = (self.ais_length / 3) * 2
        self.distal_ais.L = self.ais_length / 3
        assert (
            self.proximal_ais.L + self.distal_ais.L == self.ais_length
        ), "AIS length error!"
        self.proximal_ais.diam = 1.5
        self.distal_ais.diam = 1
        self.proximal_ais.nseg = 9
        self.distal_ais.nseg = 3

    def _setup_biophysics(self):
        """add all channels and passive properties"""
        for section in self.all_segs:
            section.insert("pas")
            section.Ra = 70
            section.cm = 1.2
            section.g_pas = 1 / 30000
            section.e_pas = -65

        for section in self.active:
            section.insert("na")
            section.insert("kd")
            section.ek = -90
            section.ena = 60

        for section in self.passive:
            for seg in section:
                seg.pas.g = 0.001
                seg.pas.e = -65

        for myelin_section in self.myelinated_segs_list:
            for myelin_seg in myelin_section:
                myelin_seg.cm = 0.012
                myelin_seg.g_pas = 1 / 100000

        for node_section in self.nodes_list:
            for node_seg in node_section:
                node_seg.g_pas = 1 / 1000
                node_seg.gbar_na = 10115
                node_seg.gbar_kd = 100

    def add_stim(self, stim_dict):
        self.stim_dict = stim_dict
        self.stim_what = self.get_section(stim_dict["thing_to_stim"])
        self.stim = h.IClamp(self.stim_what(stim_dict["loc"]))
        self.stim.delay = stim_dict["delay"]
        self.stim.dur = stim_dict["dur"]
        self.stim.amp = stim_dict["amp"]
        self.experiment_temperature = stim_dict["experiment_temperature"]


    def run(self):
        h.celsius = self.experiment_temperature
        t = h.Vector().record(h._ref_t)
        h.finitialize(self.stim_dict["rmp"] * mv)
        h.continuerun(self.stim_dict["run_dur"] * ms)
        self.stim_dict["t"] = np.asarray(t)
        return self.stim_dict

    def get_section(self, thing):
        for item in self.all_segs:
            if item.name().endswith(thing):
                return item
        else:
            print(f"section {thing} was not found. Available sections are {self.all}")
            raise IndexError("couldn't find it")

    def __repr__(self):
        return f"MitralCell[{self._uid}]"
