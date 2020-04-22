import numpy as np
from neuron import h
from neuron.units import ms
from neuron.units import mV as mv


h.load_file('stdrun.hoc')
h.nrn_load_dll("../../hoc")

class MitralCell():
    def __init__(self,uid):
        self._uid = uid
        self.stim_what = ""
        self.stim_dict = {}
        self.celsius = 23
        self.myelinated_segs = 10
        self.nodes = self.myelinated_segs -1
        self.ais_length = 30
        self._define_morphology()
        self._setup_morphology()
        self._setup_biophysics()

    def _define_morphology(self):
        self.soma = h.Section(name='soma', cell=self)
        self.dend = h.Section(name='dend', cell=self)
        self.proximal_ais = h.Section(name = "proximal_ais", cell=self)
        self.distal_ais = h.Section(name = "distal_ais", cell=self)

        self.active = [self.soma, self.proximal_ais, self.distal_ais] # ref to active components
        self.passive = [self.dend] # ref to passive components
        self.all_segs = self.active + self.passive

    def _setup_morphology(self):
        self.dend.connect(self.soma(1))
        self.proximal_ais.connect(self.soma(0.5))
        self.distal_ais.connect(self.proximal_ais(1))
        self.soma.L = 20
        self.soma.diam = 20
        self.soma.nseg = 3
        self.dend.L = 200
        self.dend.diam = 5
        self.dend.nseg = 15
        self.proximal_ais.L = (self.ais_length/3)*2
        self.distal_ais.L = (self.ais_length/3)
        assert self.proximal_ais.L + self.distal_ais.L == self.ais_length, "AIS length error!"
        self.proximal_ais.diam = 1.5
        self.distal_ais.diam = 1
        self.proximal_ais.nseg = 9
        self.distal_ais.nseg = 3

    def _setup_biophysics(self):
        for section in self.all_segs:
            section.insert('pas')
            section.insert('na')
            section.insert('kd')
            section.Ra = 70
            section.cm = 1.2
            section.g_pas = 1/30000
            section.e_pas = -65
            section.ek = -90
            section.ena = 60

        for section in self.active:
            section.insert('hh')

        for section in self.active:
            for seg in section:
                seg.hh.gnabar = 0.12
                seg.hh.gkbar = 0.036
                seg.hh.gl = 0.0003
                seg.hh.el = -54.3
        for section in self.passive:
            for seg in section:
                seg.pas.g = 0.001
                seg.pas.e = -65

    def add_stim(self, stim_dict):
        self.stim_dict = stim_dict
        self.stim_what = self.get_section(stim_dict['thing_to_stim'])
        self.stim = h.IClamp(self.stim_what(stim_dict['loc']))
        self.stim.delay = stim_dict['delay']
        self.stim.dur = stim_dict['dur']
        self.stim.amp = stim_dict['amp']

    def run(self):
        t = h.Vector().record(h._ref_t)
        h.finitialize(self.stim_dict['rmp']*mv)
        h.continuerun(self.stim_dict['run_dur']*ms)
        self.stim_dict['t']=np.asarray(t)
        return self.stim_dict

    def get_section(self, thing):
        for item in self.all_segs:
            if item.name().endswith(thing):
                return item
        else:
            print(f"section {thing} was not found. Available sections are {self.all}")
            raise IndexError("couldn't find it")
    def __repr__(self):
        return f'MitralCell[{self._uid}]'
