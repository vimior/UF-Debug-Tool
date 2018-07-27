#!/usr/bin/env python

import sys
import numpy as np


class GCodeBuilder:
    """
    Build a GCode instruction set.
    """
    def __init__(self, options):
        self.codes = []
        self.config = options
        self.drawing = False
        self.last = None
        self.position = None

        self.preamble = [
            'G0 X{x_home} Y{y_home} Z{z_home} F{moving_feedrate}'
        ]
        self.sheet_footer = [
            'G0 X{x_home} Y{y_home} Z{z_home} F{moving_feedrate}'
        ]

    def start(self):
        """
        Start drawing.
        """
        self.drawing = True

    def stop(self):
        """
        Stop drawing.
        """
        self.drawing = False

    def go_to_point(self, x, y, stop=False):
        """
        Move the print head to a certain point.
        """
        if self.last == (x, y):
            return

        if stop:
            return
        else:
            if self.drawing: 
                self.stop()
            cmd = 'G0 X{0:.2f} Y{1:.2f}'.format(y, -x)
            cmd += ' Z{z_offset_pen_up} F{moving_feedrate}'
            self.codes.append(cmd)
            cmd = 'G0 Z{z_offset} F{moving_feedrate}'
            self.codes.append(cmd)

        self.last = (x, y)

    def draw_to_point(self, x, y):
        """
        Draw to a certain point.
        """
        if self.last == (x, y):
            return

        if self.drawing is False:
            self.start()
        cmd = 'G1 X{0:.2f} Y{1:.2f}'.format(y, -x)
        cmd += ' F{drawing_feedrate}'
        self.codes.append(cmd)

        self.last = (x, y)

    def draw_polyline(self, points):
        """
        Draw a polyline (series of points).
        """
        start = points[0]

        self.go_to_point(start[0], start[1])
        self.start()

        for point in points[1:]:
            self.draw_to_point(point[0], point[1])
            self.last = point
        self.draw_to_point(start[0], start[1])  # add

        cmd = 'G0 Z{z_offset_pen_up} F{moving_feedrate}'
        self.codes.append(cmd)
        self.stop()

    def build(self):
        """
        Build complete GCode and return as string. 
        """
        commands = []
        commands.extend(self.preamble)
        commands.extend(self.codes)
        commands.extend(self.sheet_footer)
        if self.config.get('return_template', False):
            return '\n'.join(commands)
        else:
            return '\n'.join(commands).format(
                x_home=self.config.get('x_home', 150),
                y_home=self.config.get('y_home', 0),
                z_home=self.config.get('z_home', 90),
                z_offset=self.config.get('z_offset', 90),
                z_offset_pen_up=self.config.get('z_offset', 90) + self.config.get('pen_up', 0),
                moving_feedrate=self.config.get('moving_feedrate', 1000),
                drawing_feedrate=self.config.get('drawing_feedrate', 150),
            )
