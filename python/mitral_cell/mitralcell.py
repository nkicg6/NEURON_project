import numpy as np
from neuron import h
from neuron.units import ms
from neuron.units import mV as mv


h.load_file('stdrun.hoc')

class MitralCell():
    def __init__(self,uid):
        self._uid = uid
        self._setup_morphology()
        self._setup_biophysics()
        self.stim_what = ""
        self.stim_dict = {}

    def _setup_morphology(self):
        self.soma = h.Section(name='soma', cell=self)
        self.dend = h.Section(name='dend', cell=self)
        self.ais = h.Section(name = "ais", cell=self)
        self.active = [self.soma, self.ais] # ref to active components
        self.passive = [self.dend] # ref to passive components

        self.all = self.active + self.passive
        self.dend.connect(self.soma(0.5))
        self.ais.connect(self.soma(0.5))
        self.soma.L = 12.6157
        self.soma.diam = 12.6157
        self.soma.nseg = 3
        self.dend.L = 200
        self.dend.diam = 1
        self.dend.nseg = 15
        self.ais.L = 25
        self.ais.diam = 0.5
        self.ais.nseg = 9

    def _setup_biophysics(self):
        for section in self.all:
            section.Ra = 100
            section.cm = 1
        for section in self.active:
            section.insert('hh')
        for section in self.passive:
            section.insert('pas')

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

        print(f"adding current clamp stimulation to {self.stim_what}")
        self.stim = h.IClamp(self.stim_what(stim_dict['loc']))
        self.stim.delay = stim_dict['delay']
        self.stim.dur = stim_dict['dur']
        self.stim.amp = stim_dict['amp']

    def run(self):
        print(f'running with parameters: {self.stim_dict}')
        t = h.Vector().record(h._ref_t)
        h.finitialize(self.stim_dict['rmp']*mv)
        h.continuerun(self.stim_dict['run_dur']*ms)
        self.stim_dict['t']=np.asarray(t)
        return self.stim_dict

    def get_section(self, thing):
        for item in self.all:
            if item.name().endswith(thing):
                return item
        else:
            print(f"section {thing} was not found. Available sections are {self.all}")
            raise IndexError("couldn't find it")
    def __repr__(self):
        return f'MitralCell[{self._uid}]'
