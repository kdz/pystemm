## The View class is the main interface from PySTEMM models to OmniGraffle, via appscript

import appscript

## "k", from appscript module, produces property-dict keys that OmniGraffle understands
## e.g. {k.color: "Green"}

K = appscript.k

## View Uses the appscript module to communicate with the separate OmniGraffle app
## Most drawing information is via "property" dicts e.g. {k.color: ....}

class View(object):
    def __init__(self):

        ## Start up OmniGraffle with a blank "Untitled" doc to draw on
        self.OG = appscript.app(id="com.omnigroup.OmniGrafflePro")
        self.OG.launch()
        existing_doc = self.OG.documents['Untitled']
        self.doc = existing_doc.get() if existing_doc.exists() else self.OG.make(new=K.document).get()

        ## keep a reference to the OmniGraffle canvas, to use for all drawing
        self.canvas = self.doc.canvases.first.get()

        ## keep a dictionary of model_object to OmniGraffle shape
        ## ... needed to later draw edges(model_objectA, model_objectB, ...)
        self.model_object_to_solid = {}

        ## just keep lists of nodes and edges, until draw() is called
        self.nodes = []
        self.edges = []
        self.leafEdges = []

        self.instanceStencil = self._getInstanceStencil()   ## This is a work-around for OmniGraffle bug
        self.layout(Force_Directed_Layout_Props)

    def layout(self, layoutProps):
        self._layout = layoutProps

    def _getInstanceStencil(self):
        ## Workaround for OmniGraffle bug
        ## locate the "instance" shape from the master "stencil.graffle" file
        import os
        my_dir = os.path.dirname(__file__)
        stencil_file = my_dir + '/stencil.graffle'
        return self.OG.open(stencil_file).canvases.first.solids.first.get()

    def node(self, model_object, node_props):
        ## add the node to the node list (to draw later)
        self.nodes.append((model_object, node_props))

    def edge(self, model_object1, model_object2, line_props, label_props):
        ## add the edge to the edge list (to draw later)
        self.edges.append((model_object1, model_object2, line_props, label_props))

    def leafEdgeAndNode(self, x, y, lineProps, labelProps, targetProps):
        ## Add the leaf Edge & Node (i.e. not be added to model_object_to_solid dict) to draw later
        self.leafEdges.append((x, y, lineProps, labelProps, targetProps))

    def draw(self):
        ## draw the nodes, do 1st layout, draw all edges, do another layout
        for n in self.nodes: self._drawNode(*n)
        self._do_layout()
        for e in self.edges: self._drawEdge(*e)
        for e in self.leafEdges: self._drawLeafEdgeAndNode(*e)
        self._do_layout()

    def _drawNode(self, model_object, node_props):
        ## only draw nodes once, by checking model_object_to_solid dict
        if model_object not in self.model_object_to_solid:
            solid = self._drawLeafNode(node_props)
            self.model_object_to_solid[model_object] = solid

    def _drawEdge(self, model_object1, model_object2, line_props, label_props):
        line = self.canvas.connect(self.model_object_to_solid[model_object1],
                                   to=self.model_object_to_solid[model_object2],
                                   with_properties=line_props)
        self._addLabel(line, label_props)

    def _drawLeafNode(self, node_props):
        if node_props.get(K.stencil_name):
            s = self._clone_from_stencil(node_props.get(K.stencil_name))
            props = sanitize_og_props(node_props)
            for key, val in props.items():
                getattr(s, key.name).set(val)
        else:
            s = self.canvas.make(new=K.shape,
                                 at=self.canvas.graphics.end,
                                 with_properties=node_props)
        return s

    def _addLabel(self, line, label_props):
        ## add a label to a line
        if not label_props == {}:
            self.canvas.make(new=K.label, at=line.labels.end,
                             with_properties=label_props)

    def _drawLeafEdgeAndNode(self, x, y, lineProps, labelProps, targetProps):
        s = self._drawLeafNode(targetProps)
        l = self.canvas.connect(self.model_object_to_solid[x], to=s, with_properties=lineProps)
        self._addLabel(l, labelProps)
        return l

    def _clone_from_stencil(self, stencil_name):
        ## Workaround for OmniGraffle bug: make a copy for an "instance" shape
        self.instanceStencil().duplicate(to=self.canvas.graphics.end)
        s = self.canvas.graphics.last.get()
        return s

    def _do_layout(self):
        lay = self.canvas.layout_info
        lay.properties.set(self._layout)
        self.canvas.layout()


def sanitize_og_props(props):
    # Workaround for OmniGraffle Bug that forces instance-shapes (small, with text offset outside)
    # to be cloned from a stencil rather than createdly directly from code
    props = dict(props)
    if K.stencil_name in props:
        for key in props.keys():
            if key in (K.autosizing,):
                del props[key]
        del props[K.stencil_name]
    return props

## These two property dicts can be passed to OmniGraffle to get 2 kinds of automatic layout

Force_Directed_Layout_Props = {K.type: K.force_directed,
                               K.force_directed_line_length: 0.5,
                               K.force_directed_separation: 0.3,
                               K.automatic_layout: False}
Hierarchical_Layout_Props = {K.type: K.hierarchical,
                             K.direction: K.left_to_right,
                             K.rank_separation: 0.5,
                             K.object_separation: 0.25}
