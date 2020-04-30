# channel mod definitions from Hu et al. 2009 doi:10.1038/nn.2359
# TODO! edit channel biophysics based on https://senselab.med.yale.edu/ModelDB/showmodel?model=263053&file=/zbili_debanne/myelinated_axon_1.hoc#tabs-2
# TODO! add Kd channel
# TODO! Firing is odd (no bursting). Figure out why, it must be channel kinetics.

import numpy as np
from neuron import h
from neuron.units import ms
from neuron.units import mV as mv


h.load_file("stdrun.hoc")

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
        self.gnav12_dist = {"min":0, "max":2000, "reverse":True}
        self.gnav16_dist =  {"min":0, "max":2000, "reverse":False}
        h.celsius = self.experiment_temperature
        self._define_morphology()
        self._setup_morphology()
        self.setup_biophysics()

    def _make_ais(self):
        self.ais = h.Section(name="ais")

    def _make_myelinated_segments(self):
        for n in range(self.n_myelinated_segs):
            self.myelinated_segs_list.append(h.Section(name=f"myelin_seg_{n}"))

    def _make_nodes(self):
        for n in range(self.n_nodes):
            self.nodes_list.append(h.Section(name=f"node_{n}"))

    def _define_morphology(self):
        self.soma = h.Section(name="soma")
        self.dend = h.Section(name="dend")
        self._make_ais()
        self._make_myelinated_segments()
        self._make_nodes()
        self.active = [self.soma, self.ais, *self.nodes_list]
        self.passive = [self.dend, *self.myelinated_segs_list]
        self.all_segs = self.active + self.passive

    def _setup_morphology(self):
        self.dend.connect(self.soma, 0, 1)
        self.ais.connect(self.soma,1)
        self.myelinated_segs_list[0].connect(self.ais, 1)
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
        self.ais.L = self.ais_length
        self.ais.diam = 1.5
        self.ais.nseg = 15

    def setup_biophysics(self):
        """add all channels and passive properties"""
        self._uniform_passive_biophysics()
        self._ais_biophysics()
        self._soma_biophysics()
        self._node_biophysics()
        self._dendrite_biophysics()
        self._myelinated_segments_biophysics()

    def _uniform_passive_biophysics(self):
        """adds universal passive properties/leak properties. can be updated individually per segment as well. Must be called first."""
        for section in self.all_segs:
            section.insert("pas")
            section.Ra = 150
            section.cm = 1.0
            section.g_pas = 0.0000333
            section.e_pas = -69.5

    def _soma_biophysics(self):
        """setup biophysics for soma. All segments are equal for now."""
        self.soma.insert("na12")
        self.soma.insert("kv")
        self.soma.cm = 1
        self.soma.Ra = 150
        self.soma.gbar_na12 = 80
        self.soma.ena = 60
        self.soma.gbar_kv = 20
        self.soma.ek = -90

    def _dendrite_biophysics(self):
        """setup biophysics for dendrites. All segments are equal for now."""
        self.dend.insert("na12")
        self.dend.insert("kv")
        self.dend.gbar_na12 = 80
        self.dend.ena=60
        self.dend.gbar_kv=10
        self.dend.ek=-90

    def _ais_biophysics(self):
        """setup biophysics for ais. Channel distributions will be defined as gradients along segments."""
        self.ais.insert("na12")
        self.ais.insert("na16")
        self.ais.insert("kv")
        na12_gradient = self.simple_ais_channel_gradient(self.gnav12_dist)
        na16_gradient = self.simple_ais_channel_gradient(self.gnav16_dist)
        for ind, seg in enumerate(self.ais):
            seg.gbar_na16 = na16_gradient[ind]
        for ind, seg in enumerate(self.ais):
            seg.gbar_na12 = na12_gradient[ind]

        self.ais.gbar_kv = 100

    def _myelinated_segments_biophysics(self):
        for myelin_section in self.myelinated_segs_list:
            for myelin_seg in myelin_section:
                myelin_seg.cm = 0.012
                myelin_seg.g_pas = 1 / 100000

    def _node_biophysics(self):
        for node_section in self.nodes_list:
            node_section.insert("na16")
            #node_section.insert("kd")
            for node_seg in node_section:
                node_seg.g_pas = 0.0000333
                #node_seg.Ra = 150
                node_seg.gbar_na16 = 2000
                node_seg.ena=60
                #node_seg.gbar_kd = 0.00855
                #node_seg.ek = -90
                node_seg.e_pas = -38.3

    def simple_ais_channel_gradient(self,gmap):
        """temporary method. Uses a linear increase or decrease of channel density based on nseg. Need to make it more realistic based on Hu et al. 2009 Figure 5"""
        a = np.linspace(gmap["min"], gmap["max"], self.ais.nseg)
        if gmap["reverse"] == True:
            return a[::-1]
        return a

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
        str_rep = f"MitralCell[{self._uid}] with {self.n_nodes} nodes of ranvier, {self.n_myelinated_segs} myelinated segments, and a {self.ais_length}\u03BCm AIS."
        return str_rep
