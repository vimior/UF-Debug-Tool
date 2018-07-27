#!/usr/bin/env python

from lxml import etree

from .svglib import bezmisc
from .svglib import cubicsuperpath
from .svglib import ffgeom
from .svglib import inkex
from .svglib import simplepath
from .svglib import simpletransform

from collections import namedtuple
Point_Tuple = namedtuple('Point_Tuple', ('b0', 'b1', 'b2', 'b3'))
Point = namedtuple('Point', ('x', 'y'))

import six
if six.PY3:
    basestring = str


class SvgEntity(object):
    """
    Base class for SVG entities.
    """
    def __init__(self, node, node_transform):
        pass


class SvgIgnored(SvgEntity):
    """
    An SVG entity which will not be rendered.
    """
    def __init__(self, node, node_transform):
        self.tag = node.tag


class SvgPath(SvgEntity):
    """
    An SVG entity which will render a segmented line.
    """
    def __init__(self, node, node_transform):
        d = node.get('d')

        path = simplepath.parsePath(d)

        if len(path) == 0:
            return
        
        path = cubicsuperpath.CubicSuperPath(path)
        simpletransform.applyTransformToPath(node_transform, path)

        # path is now a list of lists of cubic beziers [ctrl p1, ctrl p2, endpoint]
        # where the start-point is the endpoint of the previous segment
        self.segments = []
        
        for cubic_bezier_path in path:
            points = []
            
            self._subdivide_cubic_bezier_path(cubic_bezier_path, 0.2)    # TODO: smoothness preference

            for p1, p2, endpoint in cubic_bezier_path:
                points.append(p2)
            
            self.segments.append(points)

    def _compute_max_distance(self, points):
        """
        Compute the max distance between four points.
        """
        ((p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)) = points

        p0 = ffgeom.Point(p0x, p0y)
        p1 = ffgeom.Point(p1x, p1y)
        p2 = ffgeom.Point(p2x, p2y)
        p3 = ffgeom.Point(p3x, p3y)

        s1 = ffgeom.Segment(p0, p3)

        return max(s1.distanceToPoint(p1), s1.distanceToPoint(p2))

    def _subdivide_cubic_bezier_path(self, cubic_bezier_path, flat):
        """
        Break up a bezier curve into smaller curves, each of which
        is approximately a straight line within a given tolerance
        (the "smoothness" defined by [flat]).

        This is a modified version of Inkscape's cspsubdiv.cspsubdiv().
        The recursive call has been rewritten because it caused
        recursion-depth errors on complicated line segments.
        """
        i = 1

        while True:
            while True:
                if i >= len(cubic_bezier_path):
                    return

                # First bezier, first control point 
                p0 = cubic_bezier_path[i - 1][1]

                # First bezier, endpoint
                p1 = cubic_bezier_path[i - 1][2]

                # Second bezier, Second control point
                p2 = cubic_bezier_path[i][0]

                # Second bezier, first control point
                p3 = cubic_bezier_path[i][1]

                # b = (p0, p1, p2, p3)
                b = Point_Tuple(Point(p0[0], p0[1]), Point(p1[0], p1[1]), Point(p2[0], p2[1]), Point(p3[0], p3[1]))

                if self._compute_max_distance(b) > flat:
                    break

                i += 1

            one, two = bezmisc.beziersplitatt(b, 0.5)
            cubic_bezier_path[i - 1][2] = one[1]
            cubic_bezier_path[i][0] = two[2]
            p = [one[2], one[3], two[1]]
            cubic_bezier_path[i:1] = [p]

    def new_path_from_node(self, node):
        newpath = etree.Element(inkex.addNS('path', 'svg'))

        node_style = node.get('style')
        
        if node_style:
            newpath.set('style', node_style)
        
        transform = node.get('transform')
        
        if transform:
            newpath.set('transform', transform)
        
        return newpath


class SvgRect(SvgPath):
    """
    An SVG entity will render a rectangle.
    """
    def __init__(self, node, node_transform):
        newpath = self.new_path_from_node(node)

        x = float(node.get('x'))
        y = float(node.get('y'))
        width = node.get('width')
        if width.endswith("%"):
            w = float(width[:-1])
        else:
            w = float(width)
        height = node.get('height')
        if height.endswith("%"):
            h = float(height[:-1])
        else:
            h = float(height)
        # w = float(node.get('width'))
        # h = float(node.get('height'))

        a = []
        a.append(['M ', [x, y]])
        a.append([' l ', [w, 0]])
        a.append([' l ', [0, h]])
        a.append([' l ', [-w, 0]])
        a.append([' Z', []])

        newpath.set('d', simplepath.formatPath(a))
        
        SvgPath.__init__(self, newpath, node_transform)


class SvgLine(SvgPath):
    """
    An SVG entity that renders a line.
    """
    def __init__(self, node, node_transform):
        newpath = self.new_path_from_node(node)

        x1 = float(node.get('x1'))
        y1 = float(node.get('y1'))
        x2 = float(node.get('x2'))
        y2 = float(node.get('y2'))

        a = []
        a.append(['M ', [x1, y1]])
        a.append([' L ', [x2, y2]])

        newpath.set('d', simplepath.formatPath(a))
        
        SvgPath.__init__(self, newpath, node_transform)


class SvgPolyLine(SvgPath):
    """
    An SVG entity that renders as a segmented line.
    """
    def __init__(self, node, node_transform):
        newpath = self.new_path_from_node(node)
        pl = node.get('points', '').strip()

        if pl == '':
            return
        
        pa = pl.split()
        
        if not len(pa):
            return

        d = "M " + pa[0]
        
        for i in range(1, len(pa)):
            d += " L " + pa[i]
        
        newpath.set('d', d)
        
        SvgPath.__init__(self, newpath, node_transform)


class SvgEllipse(SvgPath):
    """
    An SVG entity that renders an ellipse.
    """
    def __init__(self, node, node_transform):
        rx = float(node.get('rx', '0'))
        ry = float(node.get('ry', '0'))

        newpath = self.make_ellipse_path(rx, ry, node)
        
        SvgPath.__init__(self, newpath, node_transform)

    def make_ellipse_path(self, rx, ry, node):
        if rx == 0 or ry == 0:
            return None
        
        cx = float(node.get('cx', '0'))
        cy = float(node.get('cy', '0'))

        x1 = cx - rx
        x2 = cx + rx

        d = 'M %f,%f ' % (x1, cy) + \
            'A %f,%f ' % (rx, ry) + \
            '0 1 0 %f, %f ' % (x2, cy) + \
            'A %f,%f ' % (rx, ry) + \
            '0 1 0 %f,%f' % (x1, cy)

        newpath = self.new_path_from_node(node)
        newpath.set('d', d)

        return newpath


class SvgCircle(SvgEllipse):
    """
    An SVG entity that renders as an ellipse.
    """
    def __init__(self, node, node_transform):
        rx = float(node.get('r', '0'))

        newpath = self.make_ellipse_path(rx, rx, node)

        SvgPath.__init__(self, newpath, node_transform)


class SvgText(SvgIgnored):
    """
    An SVG entity that renders as text.
    """
    def __init__(self, node, node_transform):
        print('unable to draw text. please convert it to a path first.')

        SvgIgnored.__init__(self, node, node_transform)


class SvgLayerChange(SvgEntity):
    """
    An SVG entity that stands in for a delay between layer changes.
    """
    def __init__(self, layer_name):
        self.layer_name = layer_name


class SvgParser(object):
    """
    Parses an SVG.
    """
    entity_map = {
        'path': SvgPath,
        'rect': SvgRect,
        'line': SvgLine,
        'polyline': SvgPolyLine,
        'polygon': SvgPolyLine,
        'circle': SvgCircle,
        'ellipse': SvgEllipse,
        'pattern': SvgIgnored,
        'metadata': SvgIgnored,
        'defs': SvgIgnored,
        'eggbot': SvgIgnored,
        ('namedview', 'sodipodi'): SvgIgnored,
        'text': SvgText
    }

    def __init__(self, svg):
        self.svg = svg
        self.entities = []

    def parseLengthWithUnits(self, attr):
        """ 
        Parse an SVG value which may or may not have units attached
        This version is greatly simplified in that it only allows: no units,
        units of px, and units of %.    Everything else, it returns None for.
        There is a more general routine to consider in scour.py if more
        generality is ever needed.
        """
        unit = 'px'
        attr = attr.strip()
        # print("attr: {}".format(attr))
        if attr[-2:] == 'px' \
            or attr[-2:] == 'pt' \
                or attr[-2:] == 'px':
            attr = attr[:-2]
        elif attr[-1:] == '%':
            unit = '%'
            attr = attr[:-1]

        try:
            value = float(attr)
        except:
            return None, None
        
        return value, unit

    def getLength(self, name, default):
        """ 
        Get the <svg> attribute with name "name" and default value "default"
        Parse the attribute into a value and associated units.    Then, accept
        no units (''), units of pixels ('px'), and units of percentage ('%').
        """
        attr = self.svg.get(name)
        
        if attr:
            value, unit = self.parseLengthWithUnits(attr)
            if not value:
                # Couldn't parse the value
                return None
            elif (unit == '') or (unit == 'px') or (unit == 'mm') or (unit == 'pt'):
                # print ("name: {}, unit: {}".format(name, unit))
                return value
            elif unit == '%':
                return float(default) * value / 100.0
            else:
                # Unsupported units
                return None
        else:
            # No width specified; assume the default value
            return float(default)

    def parse(self):
        """
        Parse the SVG data into entities.
        """
        # 0.28222 scale determined by comparing pixels-per-mm in a default Inkscape file.
        # print ("Width: {}" .format(self.getLength('width', 354)))

        # width = self.getLength('width', 354) * 0.28222
        # height = self.getLength('height', 354) * 0.28222
        #
        # self.recursivelyTraverseSvg(
        #     self.svg,
        #     [
        #         [0.28222, 0.0, -(width / 2.0)],
        #         [0.0, -0.28222, (height / 2.0)]
        #     ])

        width = self.getLength('width', 800) * 0.62 # 0.522
        height = self.getLength('height', 400) * 0.62 # 0.522
        self.recursivelyTraverseSvg(
            self.svg,
            [
                [0.62, 0.0, -(width / 2.0)],
                [0.0, -0.62, (height / 2.0)]
            ])

    def recursivelyTraverseSvg(self, nodeList, current_transform=[[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]], parent_visibility='visible'):
        """
        Recursively traverse the svg file to plot out all of the
        paths. The function keeps track of the composite transformation
        that should be applied to each path.

        This function handles path, group, line, rect, polyline, polygon,
        circle, ellipse and use (clone) elements. Notable elements not
        handled include text. Unhandled elements should be converted to
        paths in Inkscape.
        """
        for node in nodeList:
            # Ignore invisible nodes
            node_visibility = node.get('visibility', parent_visibility)

            if node_visibility == 'inherit':
                node_visibility = parent_visibility

            if node_visibility == 'hidden' or node_visibility == 'collapse':
                pass

            # Apply the current matrix transform to this node's transform
            node_transform = simpletransform.composeTransform(current_transform, simpletransform.parseTransform(node.get('transform')))

            # Root and group tags
            if node.tag == inkex.addNS('g', 'svg') or node.tag == 'g':
                if (node.get(inkex.addNS('groupmode', 'inkscape')) == 'layer'):
                    layer_name = node.get(inkex.addNS('label', 'inkscape'))
                    
                    self.entities.append(SvgLayerChange(layer_name))
                
                self.recursivelyTraverseSvg(node, node_transform, parent_visibility=node_visibility)
            # Use tags
            elif node.tag == inkex.addNS('use', 'svg') or node.tag == 'use':
                refid = node.get(inkex.addNS('href', 'xlink'))
                
                if refid:
                    # [1:] to ignore leading '#' in reference
                    path = '//*[@id="%s"]' % refid[1:]
                    refnode = node.xpath(path)
                    
                    if refnode:
                        x = float(node.get('x', '0'))
                        y = float(node.get('y', '0'))
                        
                        if (x != 0) or (y != 0):
                            node_transform = simpletransform.composeTransform(node_transform, simpletransform.parseTransform('translate(%f,%f)' % (x, y)))
                        
                        # TODO: this looks unnecessary
                        node_visibility = node.get('visibility', node_visibility)

                        self.recursivelyTraverseSvg(refnode, node_transform, parent_visibility=node_visibility)
            elif not isinstance(node.tag, basestring):
                pass
            # Entity tags
            else:
                entity = self.make_entity(node, node_transform)
                
                if entity == None:
                    pass
                    # print('unable to draw object, please convert it to a path first.')

    def make_entity(self, node, node_transform):
        """
        Construct an appropriate entity for this SVG node.
        """
        for nodetype in SvgParser.entity_map.keys():
            tag = nodetype
            ns = 'svg'
            
            if type(tag) is tuple:
                tag = nodetype[0]
                ns = nodetype[1]
            
            if node.tag == inkex.addNS(tag, ns) or node.tag == tag:
                cls = SvgParser.entity_map[nodetype]

                entity = cls(node, node_transform)
                self.entities.append(entity)
                
                return entity
        
        return None


