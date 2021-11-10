#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file file.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 18:55

import os
import traitlets
from traitlets import Unicode, Int
from .gsink import GDataSink


class MultiFilesSink(GDataSink):
    name = Unicode(default_value='multifilessink')
    duration = Int(default_value=600, min=1, max=3600, help='Max. amount of time per file').tag(config=True)
    maxfiles = Int(default_value=200, min=1, max=1000, help='Maximum number of files to keep on disk.').tag(config=True)
    location = Unicode(default_value='', allow_none=False, help='Format string pattern for the location of the files to write').tag(config=True)

    @traitlets.validate('location')
    def _check_location(self, proposal):
        path = proposal['value']
        if not os.access(os.path.dirname(path), os.X_OK):
            raise RuntimeError(f'Cannot operate {path} permission!')
        os.makedirs(path, exist_ok=True)
        return path

    def gst_pipe(self):
        return [
            f'splitmuxsink muxer=qtmux max-size-time={self.duration * 1000000000} max-files={self.maxfiles} location="{self.location}/%03d.mp4"',
        ]
