#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gstmain.py
# @brief
# @author QRS
# @version 1.0
# @date 2021-11-10 19:42

import sys, signal, traceback # noqa
import logging
from logging.handlers import RotatingFileHandler
import traitlets
from traitlets.config.application import Application
from traitlets import Bool, Unicode, List, Dict, Enum

from jetrep.stream.source import USBCamera, CSICamera
from jetrep.stream.convert import GH264CodecCvt
from jetrep.stream.sink import ShareMemorySink, MultiFilesSink, SRSRtmpSink

import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)


class GstPipelineApp(Application):
    """
    This is a gstream pipleline application.
    """
    name = Unicode('GstPipeline')
    description = Unicode(__doc__)
    config_file = Unicode('', help='Load this config file').tag(config=True)
    log_file = Unicode('/tmp/gstpipe.log', help='Write log to file ').tag(config=True)

    camera = Enum((0,1,'CSI', 'USB'), default_value=1, help='Set the video camera device').tag(config=True)
    shmsink = Bool(default_value=True, help='Use shared memory sink source').tag(config=True)
    rtmpsink = Bool(default_value=False, help='Sends FLV content to a server via RTMP').tag(config=True)
    filesink = Bool(default_value=False, help='Write stream to files').tag(config=True)

    classes = List([USBCamera, CSICamera, GH264CodecCvt, ShareMemorySink, MultiFilesSink, SRSRtmpSink])

    aliases = Dict(
        dict(
            c='GstPipelineApp.config_file'
        )
    )

    flags = Dict(
        dict(
            debug=({'GstPipelineApp': {'log_level': 10}}, 'Set loglevel to DEBUG'),
            csi=({'GstPipelineApp': {'camera': 0}}, 'Use the csi camera'),
            usb=({'GstPipelineApp': {'camera': 1}}, 'Use the usb camera'),
            rtmpsink=({'GstPipelineApp': {'rtmpsink': True}}, 'Videos to RTMP Server'),
            filesink=({'GstPipelineApp': {'filesink': True}}, 'Videos to OS disks')
        )
    )

    @traitlets.default('log')
    def _log_default(self):
        log = logging.getLogger(self.__class__.__name__)
        # log.setLevel(self.log_level)
        log.setLevel(logging.DEBUG)
        formatter = self._log_formatter_cls(fmt=self.log_format, datefmt=self.log_datefmt)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        filelog = RotatingFileHandler(
                self.log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
        filelog.setFormatter(formatter)
        log.addHandler(console)
        log.addHandler(filelog)
        return log

    def initialize(self, argv=None):
        self.parse_command_line(argv)
        if self.config_file:
            self.load_config_file(self.config_file)

    def setup(self):
        self.log.info('Setup components')
        if self.camera in ('1', 'USB'):
            cam = USBCamera(parent=self)
        else:
            cam = CSICamera(parent=self)

        if self.shmsink:
            _ = ShareMemorySink(cam, parent=self) # noqa

        if self.rtmpsink or self.filesink:
            h264cvt = GH264CodecCvt(cam, parent=self)
            if self.rtmpsink:
                _ = SRSRtmpSink(h264cvt, parent=self)
            if self.filesink:
                _ = MultiFilesSink(h264cvt, parent=self) # noqa

        self.gst_str = cam.gst_str()
        self.log.info(f'Gst string: {self.gst_str}')

    def start(self):
        self.log.info('Starting...')

        self.start_launch()

    def stop(self):
        self.log.info('Stoped.')
        self.stop_launch()

    def start_launch(self):
        self.log.info('Start gst..')
        self.gst_pipe = Gst.parse_launch(self.gst_str)
        bus = self.gst_pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message, self.mainloop)
        self.gst_pipe.set_state(Gst.State.READY)
        self.gst_pipe.set_state(Gst.State.PAUSED)
        self.gst_pipe.set_state(Gst.State.PLAYING)

    def stop_launch(self):
        self.gst_pipe.set_state(Gst.State.NULL)

    def on_message(self, bus: Gst.Bus, msg: Gst.Message, loop: GObject.MainLoop):
        self.log.info(f'Message type: {msg.type}')
        t = msg.type
        if t == Gst.MessageType.EOS:
            self.log.info('Stream EOS')
            loop.quit()
        elif t == Gst.MessageType.ERROR:
            self.log.error('{}: {}'.format(msg.parse_error()))
            loop.quit()
        elif t == Gst.MessageType.WARNING:
            self.log.warning('{}: {}'.format(msg.parse_warning()))
        return True

    def run(self, argv=None):
        try:
            self.mainloop = GObject.MainLoop()
            self.initialize(argv)
            self.setup()
            self.start()
            self.mainloop.run()
        except Exception:
            self.mainloop.quit()
            self.log.error(traceback.format_exc(limit=6))


# def signal_handler(sig, frame):
#     app.log.info('Handle signal: [%d]' % sig)
#     app.gst_pipe.set_state(Gst.State.NULL)
#     sys.exit(0)
#
#
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    app = GstPipelineApp()
    app.run()
