#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ai.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-12 22:13

import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def softmax(x, axis=None):
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / np.sum(e_x, axis=axis, keepdims=True)
