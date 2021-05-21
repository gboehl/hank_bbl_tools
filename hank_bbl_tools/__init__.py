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


def store_hank(path, hank, A, B, sr):

    F1 = A[:, :sr.n_par.nstates]
    F2 = A[:, sr.n_par.nstates:]
    F3 = B[:, :sr.n_par.nstates]
    F4 = B[:, sr.n_par.nstates:]
    AA = np.pad(F2, ((0, 0), (sr.n_par.nstates, 0)))
    BB = np.hstack((F1, F4))
    CC = np.pad(F3, ((0, 0), (0, sr.n_par.ncontrols)))

    var_list = []
    for i in range(len(sr.indexes.distr_m)):
        var_list.append('distr_m%s' % i)

    for i in range(len(sr.indexes.distr_k)):
        var_list.append('distr_k%s' % i)

    for i in range(len(sr.indexes.distr_y)):
        var_list.append('distr_y%s' % i)

    for i in range(len(sr.indexes.D)):
        var_list.append('distr_cop%s' % i)

    for i in hank.state_names_ascii:
        var_list.append(i)

    for i in range(len(sr.indexes.Vm)):
        var_list.append('Vm%s' % i)

    for i in range(len(sr.indexes.Vk)):
        var_list.append('Vk%s' % i)

    for i in range(len(sr.indexes.V)):
        var_list.append('V%s' % i)

    for i in hank.control_names_ascii:
        var_list.append(i)

    return np.savez_compressed(path, AA=AA, BB=BB, CC=CC, var_list=var_list)
