#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gconvert.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:50

from jetrep.stream.gelement import GElement


class GDataConvert(GElement):
    def gst_pipe(self):
        return [
            ' tee name=t_%s ' % self.name
        ]
