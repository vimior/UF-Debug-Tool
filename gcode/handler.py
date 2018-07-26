#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from ._gcode.contour.parse import SVGParser


class GcodeHandler(object):
    def __init__(self, ui):
        super(GcodeHandler, self).__init__()
        self.ui = ui
        self.source = None
        self.template = None

    def svg_to_gcode(self):
        if self.source:
            parser = SVGParser(return_template=True)
            self.template = parser.convert(self.source)
        return self.template

if __name__ == '__main__':
    handler = GcodeHandler(None)
    with open('tmp.svg', 'rb') as f:
        svg_data = f.read()
    gcode = handler.svg_to_gcode(svg_data)
    # print(gcode)
    config = {
        'x_home': 150,
        'y_home': 0,
        'z_home': 90,
        'z_offset': 90,
        'pen_up': 0,
        'z_offset_pen_up': 90,
        'moving_feedrate': 1000,
        'drawing_feedrate': 150,
    }
    print(gcode.format(**config))