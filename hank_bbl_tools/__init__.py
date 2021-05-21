#!/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as np
from julia import Main as japi
from julia.Flatten import flatten, reconstruct
from julia.Serialization import serialize, deserialize


def setfield(obj, field, val):

    japi.tmp_obj = obj
    japi.eval("using Setfield")

    if isinstance(val, int):
        val = float(val)
    japi.tmp_val = val
    japi.eval("@set! tmp_obj.%s = tmp_val" % field)

    return japi.tmp_obj


def store_hank(path, hank, stst, A, B, gx=None, hx=None):

    var_list = []
    for i in range(len(stst.indexes.distr_m)):
        var_list.append('distr_m%s' % i)

    for i in range(len(stst.indexes.distr_k)):
        var_list.append('distr_k%s' % i)

    for i in range(len(stst.indexes.distr_y)):
        var_list.append('distr_y%s' % i)

    for i in range(len(stst.indexes.D)):
        var_list.append('distr_cop%s' % i)

    for i in hank.state_names_ascii:
        var_list.append(i)

    for i in range(len(stst.indexes.Vm)):
        var_list.append('Vm%s' % i)

    for i in range(len(stst.indexes.Vk)):
        var_list.append('Vk%s' % i)

    for i in range(len(stst.indexes.V)):
        var_list.append('V%s' % i)

    for i in hank.control_names_ascii:
        var_list.append(i)

    shock_states = hank.shock_names
    shocks = ['e_' + s for s in shock_states]

    f1 = A[:, :stst.n_par.nstates]
    f2 = A[:, stst.n_par.nstates:]
    f3 = B[:, :stst.n_par.nstates]
    f4 = B[:, stst.n_par.nstates:]

    rdict = {}
    if gx is not None:
        rdict['gx'] = gx
        rdict['hx'] = hx
    rdict['AA'] = np.pad(f2, ((0, 0), (stst.n_par.nstates, 0)))
    rdict['BB'] = np.hstack((f1, f4))

    CC = np.pad(f3, ((0, 0), (0, stst.n_par.ncontrols)))
    rdict['CC'] = CC

    DD = np.zeros((len(var_list), len(shocks)))
    for i, v in enumerate(shock_states):
        DD[:, shock_states.index(v)] = CC[:, list(var_list).index(v)]

    rdict['DD'] = DD
    rdict['shock_states'] = shock_states
    rdict['shocks'] = shocks

    if 'π' in var_list:
        var_list[list(var_list).index('π')] = 'Pi'
    if 'πw' in var_list:
        var_list[list(var_list).index('πw')] = 'Piw'

    rdict['vars'] = var_list

    return np.savez_compressed(path, **rdict)
