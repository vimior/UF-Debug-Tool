#!/usr/bin/env python

import os
import six
if six.PY2:
    import lxml.etree as ET
else:
    import xml.etree.ElementTree as ET
if six.PY3:
    from io import StringIO
else:
    from StringIO import StringIO

from .gcode import GCodeBuilder
from .svg import SvgLayerChange, SvgParser, SvgPath


class SVGParser(object):
    def __init__(self, *args, **kwargs):
        self.svg_path = kwargs.get('svg_path', None)
        self.gcode_path = kwargs.get('gcode_path', None)
        self.__gcode = GCodeBuilder(kwargs)

    def convert(self, svg_content):
        """
        Setup GCode writer and SVG parser.
        """
        # self.__gcode.codes = []
        if self.svg_path:
            svg_dir = os.path.dirname(self.svg_path)
            if not os.path.exists(svg_dir):
                os.makedirs(svg_dir)
            self.write_svg_to_file(svg_content, self.svg_path)

        document = self.parse_xml(svg_content)
        parser = SvgParser(document)
        parser.parse()
        # map(self.process_svg_entity, parser.entities)
        for entity in parser.entities:
            self.process_svg_entity(entity)

        output = self.__gcode.build()
        if self.gcode_path:
            gcode_dir = os.path.dirname(self.gcode_path)
            if not os.path.exists(gcode_dir):
                os.makedirs(gcode_dir)
            self.write_gcode_to_file(output, self.gcode_path)
        return output

    @staticmethod
    def write_svg_to_file(data, path):
        if six.PY3:
            if not isinstance(data, bytes):
                data = bytes(data, encoding='utf-8')
        try:
            with open(path, 'wb') as f:
                f.write(data)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def write_gcode_to_file(data, path):
        if six.PY3:
            if not isinstance(data, bytes):
                data = bytes(data, encoding='utf-8')
        try:
            with open(path, 'wb') as f:
                f.write(data)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def parse_xml(xml_content):
        """
        Parse the XML input.
        """
        utf8_parser = ET.XMLParser(encoding='utf-8')
        if six.PY3:
            if isinstance(xml_content, bytes):
                xml_content = str(xml_content, encoding='utf-8')
            tree = ET.parse(StringIO(xml_content), parser=utf8_parser)
        else:
            tree = ET.parse(StringIO(xml_content.encode('utf-8')), parser=utf8_parser)
        document = tree.getroot()

        return document

    def process_svg_entity(self, svg_entity):
        """
        Generate GCode for a given SVG entity.
        """
        if isinstance(svg_entity, SvgPath):
            # len_segments = len(svg_entity.segments)

            for i, points in enumerate(svg_entity.segments):
                # self.gcode.label('Polyline segment %i/%i' % (i + 1, len_segments))
                self.__gcode.draw_polyline(points)
        elif isinstance(svg_entity, SvgLayerChange):
            pass
