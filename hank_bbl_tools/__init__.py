#!/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as np


def add_const_var(mdict, const_var, new_var, xbar):
    """Adds a constraint variable. 

    Assumes that before adding, the system contains 

        `const_var = <equation>`

    and afterwards

        `const_var = max(xbar, new_var)`,

    with 

        `new_var = <equation>`
    """

    vv = mdict['vars']
    const_var = 'RB'
    rix = list(vv).index('RB')
    vv = np.hstack((vv, 'RN'))
    dimy = len(vv)

    AA = np.pad(mdict['AA'], ((0, 0), (0, 1)))
    BB = np.pad(mdict['BB'], ((0, 0), (0, 1)))
    CC = np.pad(mdict['CC'], ((0, 0), (0, 1)))
    DD = mdict['DD']

    BB[rix, [rix, -1]] = BB[rix, [-1, rix]]
    CC[rix, [rix, -1]] = CC[rix, [-1, rix]]
    fb0 = np.zeros(dimy)
    fc0 = np.zeros(dimy)
    fb0[rix] = 1
    fb0[-1] = -1

    # misc
    mdict['vars'] = vv
    mdict['const_var'] = const_var

    # sys matrices w/o constraint equation
    mdict['AA'] = AA
    mdict['BB'] = BB
    mdict['CC'] = CC
    mdict['DD'] = DD

    # constraint equation (MP rule)
    mdict['fb'] = -fb0
    mdict['fc'] = fc0

    mdict['x_bar'] = -1  # lower bound (relative to st.st.)

    return mdict


def hank2dict(hank, stst, A, B, gx=None, hx=None, path=None):

    var_list = []

    if hasattr(stst, "indexes"):
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

    if hasattr(stst, "indexes"):
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

    if path is not None: 
        np.savez_compressed(path, **rdict)

    return rdict


def mat2dict(path, shock_states):

    # load stuff
    AA = np.loadtxt(os.path.join(path, 'AA.txt'), delimiter=',')
    BB = np.loadtxt(os.path.join(path, 'BB.txt'), delimiter=',')
    CC = np.loadtxt(os.path.join(path, 'CC.txt'), delimiter=',')
    vv = np.loadtxt(os.path.join(path, 'list_of_vars.txt'), delimiter=',', dtype=str)

    vv = np.array([v[2:-1] for v in vv])

    # lets stick with UTF-8
    if 'π' in vv:
        vv[list(vv).index('π')] = 'Pi'
    if 'πw' in vv:
        vv[list(vv).index('πw')] = 'Piw'

    # DD is the mapping from shocks to states
    shocks = ['e_' + s for s in shock_states]

    DD = np.zeros((len(vv), len(shocks)))
    for i, v in enumerate(shock_states):
        DD[:, shock_states.index(v)] = CC[:, list(vv).index(v)]

    rdict = {}
    rdict['AA'] = AA
    rdict['BB'] = BB
    rdict['CC'] = CC
    rdict['DD'] = DD
    rdict['vars'] = vv
    rdict['shock_states'] = shock_states
    rdict['shocks'] = shocks
    
    return rdict
