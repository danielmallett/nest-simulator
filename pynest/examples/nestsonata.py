# -*- coding: utf-8 -*-
#
# nestsonata.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import warnings
import nest
import nest.raster_plot
import time
from pprint import pprint

import matplotlib.pyplot as plt

NUM_PROCESSES = 4
NUM_THREADS = 2

SYS_LINUX_SCALE = 1e6
SYS_DARWIN_SCALE = 1e9

# Set scaling of memory print
#sys_scale = SYS_LINUX_SCALE
sys_scale = SYS_DARWIN_SCALE

# Set network config
#example = '300_pointneurons'
example = 'GLIF'
simulate = False
plot = False
verbose_print = True
create_sonata_network = False  # For testing of convenience function
pre_sim_time = 10


def memory_thisjob():
    """Wrapper to obtain current memory usage"""
    nest.ll_api.sr('memory_thisjob')
    return nest.ll_api.spp() / sys_scale


start_time = time.time()

nest.ResetKernel()

if example == '300_pointneurons':
    config = '/Users/nicolai/github/sonata/examples/300_pointneurons/circuit_config.json'
    sim_config = '/Users/nicolai/github/sonata/examples/300_pointneurons/simulation_config.json'
    population_to_plot = 'internal'
elif example == 'GLIF':
    #config = '/Users/nicolai/github/nest_dev/nest_sonata/glif_nest_220/config.json'
    config = '../../nest_sonata/glif_nest_220/config.json'
    sim_config = None
    population_to_plot = 'v1'


sonata_net = nest.SonataNetwork(config, sim_config)


nest.set(overwrite_files=True,
         total_num_virtual_procs=NUM_PROCESSES * NUM_THREADS)

print("kernel number of processes:", nest.GetKernelStatus('num_processes'))
print("kernel number of threads:", nest.GetKernelStatus('local_num_threads'))

mem_ini = memory_thisjob()
start_time_create = time.time()

# Create nodes
sonata_net.Create()

end_time_create = time.time() - start_time_create
mem_create = memory_thisjob()

#print(f"Sonata NC (rank {nest.Rank()}):", sonata_connector.node_collections)

#print(f"Sonata Local NC (rank {nest.Rank()}):", sonata_connector.local_node_collections)

# Connect
start_time_connect = time.time()

sonata_net.Connect()
#print("done connecting")

end_time_connect = time.time() - start_time_connect
mem_connect = memory_thisjob()

print(f"number of connections: {nest.GetKernelStatus('num_connections'):,}")
print(f"number of neurons: {nest.GetKernelStatus('network_size'):,}")

if plot:
    s_rec = nest.Create('spike_recorder')
    s_rec.record_to = 'memory'
    nest.Connect(sonata_net.node_collections[population_to_plot], s_rec)

if simulate:
    print('simulating')

    start_time_sim = time.time()
    sonata_net.Simulate()
    end_time_sim = time.time() - start_time_sim

end_time = time.time() - start_time

if verbose_print:
    print(f"creation took: {end_time_create} s")
    print(f"connection took: {end_time_connect} s")
    if simulate:
        print(f"simulation took: {end_time_sim} s")
    print(f"all took: {end_time} s")
    print(f'initial memory: {mem_ini} GB')
    print(f'memory create: {mem_create} GB')
    print(f'memory connect: {mem_connect} GB')
    if simulate:
        print(f'number of spikes: {nest.GetKernelStatus("local_spike_counter"):,}')
    # pprint(nest.GetKernelStatus())
    # print(nest.GetConnections())


if plot:
    if not simulate:
        print("simulate must be True in order to plot")
    else:
        nest.raster_plot.from_device(s_rec)
        plt.show()


""" 
net_size = nest.GetKernelStatus('network_size')
print(nest.NodeCollection([net_size - 1]).get())
print(nest.NodeCollection([net_size]).get())
print("number of neurons: ", nest.GetKernelStatus('network_size'))
print(nest.NodeCollection(list(range(1, net_size+1))))
"""
