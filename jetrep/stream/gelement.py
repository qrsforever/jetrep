#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gelement.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:38

import traitlets
from traitlets.config.configurable import LoggingConfigurable
from traitlets import Unicode
from jetrep.utils.net import util_get_mac


class GElement(LoggingConfigurable):
    name = Unicode('')
    uuid = Unicode('', read_only=True)

    def __init__(self, pnode, *args, **kwargs):
        super(GElement, self).__init__(*args, **kwargs)
        if pnode is not None:
            pnode.children[self.name] = self
        self.pnode = pnode
        self.children = {}

    def gst_pipe(self):
        raise RuntimeError('abstract method called')

    @traitlets.default('uuid')
    def _default_uuid(self):
        return util_get_mac()

    def gst_str(self):
        gst = ' t_%s. ! queue ! ' % self.pnode.name if self.pnode else ''
        gst += ' ! '.join(self.gst_pipe())
        for _, child in self.children.items():
            gst += child.gst_str()
        return gst
