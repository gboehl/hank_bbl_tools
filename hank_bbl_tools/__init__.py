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
