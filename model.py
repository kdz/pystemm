## The Model class is the main class used to build actual PySTEMM models
## It's main public methods are addClasses, addInstances, and showXYZ

import appscript

K = appscript.k
import traits.api as TR
from traits.api import Int, String, Instance, List, Tuple, Dict, Bool, Float, Property, Callable, cached_property

from template import *
from view import *

def find(iterable):
    ## just a more readable name
    return next(iterable)

class Concept(TR.HasTraits):
    pass


class Model(object):
    def __init__(self, *conceptList):
        ## conceptList is a list of Concept classes
        self.conceptList = conceptList

        ## instanceList is instances of those concepts
        self.instanceList = []

        ## attrFilter dict {ConcepClass: listOfAttributes} to selectively show attributes
        self._attrFilter = {}

        ## model has its View, to draw on OmniGraffle
        self.view = View()

    def addClasses(self, *cs):
        self.conceptList = self.conceptList + cs

    def addInstances(self, *instances):
        self.instanceList += instances

    def attrFilter(self, klsToAttrsDict):
        self._attrFilter = klsToAttrsDict

    def _attrPassesFilter(self, kls, attrName):
        ## check if an attribute of a Concept class kls should be drawn or not
        return self._attrFilter.get(kls) is None or attrName in self._attrFilter[kls]

    def _traverseConcept(self, c, visitedList):
        ## walks around starting from Concept Class c
        ## adds nodes and edges (to View) for Concept Classes and their attribute definitions
        ## recursively traverses other related Concept Classes, including super classes
        ## uses visitedList to keep track of which classes have already been done

        if c in visitedList: return
        visitedList.append(c)
        self.view.node(c, apply_template(netClassTemplate(c), c))
        for attr_name, attr_cTrait in classTraits(c).items():
            if not self._attrPassesFilter(c, attr_name):
                continue
            if isPrimitive(attr_cTrait):
                continue
            else:
                attr = Attr(attr_name, attr_cTrait)
                self._traverseConcept(endPoint(attr.type), visitedList)
                self.view.edge(c,
                               endPoint(attr.type),
                               apply_template(Rel_Template, attr),
                               apply_template(Rel_Label_Template, attr))
        for b in c.__bases__ if hasattr(c, '__bases__') else []:
            if issubclass(b, Concept) and b is not Concept:
                self._traverseConcept(b, visitedList)
                self.view.edge(c, b, Subclass_Props, {})

    def _traverseInst(self, inst, visitedList):
        ## walks around starting from the Concept instance inst
        ## adds nodes and edges (to View) for instances and their attribute values
        ## recursively traverses other related instances via attribute values
        ## uses visitedList to keep track of which instances have already been done

        if inst in visitedList: return
        visitedList.append(inst)
        kls = type(inst)
        self.view.node(inst, apply_template(netInstanceTemplate(inst), inst))
        for key in classTraits(kls):
            val = getattr(inst, key)
            if val is None: continue
            if not self._attrPassesFilter(kls, key):
                continue
            trait = inst.trait(key)
            label = lineLabel(key)
            if isPrimitive(trait):
                pass
            elif isInstanceTrait(trait):
                self._traverseInst(val, visitedList)
                self.view.edge(inst, val, Link_Props, label)
            elif isListOfInstanceTrait(trait):
                for obj in val:
                    self._traverseInst(obj, visitedList)
                    self.view.edge(inst, obj, Link_Props, label)
            elif isListOfTupleOfInstancePrim(trait):
                for (obj, prim) in val:
                    self._traverseInst(obj, visitedList)
                    self.view.edge(inst, obj, Link_Props, {K.text: "%s(_,%s)" % (key, prim)})
            elif isListOfTupleOfPrimInstance(trait):
                for (prim, obj) in val:
                    self._traverseInst(obj, visitedList)
                    self.view.edge(inst, obj, Link_Props, {K.text: "%s(%s,_)" % (key, prim)})
            elif isCallableTrait(trait):
                self.view.leafEdgeAndNode(inst, val, Link_Props, label, apply_template(Callable_Template, val))
            else:
                self.view.leafEdgeAndNode(inst, val, Link_Props, label, apply_template(Val_Template, val))

    def displayConcepts(self):
        visitedList = []
        for c in self.conceptList:
            self._traverseConcept(c, visitedList)

    def displayInstances(self):
        visitedList = []
        for i in self.instanceList:
            self._traverseInst(i, visitedList)

    def showMethod(self, obj, name):
        method = getattr(obj, name)
        self.view.leafEdgeAndNode(obj, method, Link_Props, lineLabel(name), apply_template(Callable_Template, method))

    def showEval(self, obj, funcName, argsList, tmpl=None):
        func = getattr(obj, funcName)
        result = apply(func, argsList)
        label = "%s(%s)" % (funcName, ','.join(["%s" % arg for arg in argsList]))
        props = apply_template(mergeTemplates(tmpl, Val_Template), result)
        self.view.leafEdgeAndNode(obj, result, {K.stroke_pattern: 2, K.head_type: 'StickArrow'}, lineLabel(label),
                                  props)

    def showGraph(self, obj, func_names, param, range, *highlights):
        if isinstance(func_names, str): func_names = [func_names]
        for func_name in func_names:
            file = graph_file(obj, func_name, param, range, highlights)
            self.view.leafEdgeAndNode(obj, file, Link_Props, {K.text: func_name}, apply_template(Graph_Template, file))

    def animate(self, obj, from_to, num_pts, template_list):
        ## For Times between From and To, apply each template to obj & Time, draw result
        ## Expects a special key in each template: k.new: k.shape or k.line or ...
        ##   (so that lines can be drawn as easily as circles, rectangles, etc.)
        ## Bypasses View methods, and directly draws templates onto the Canvas
        c = self.view.canvas
        for p in range(from_to[0], from_to[1], (from_to[1] - from_to[0]) / num_pts):
            for t in template_list:
                shape_class = t[K.new]
                tmp = apply_template({key: v for key, v in t.items() if key != K.new}, obj, p)
                c.make(new=shape_class, at=c.graphics.end, with_properties=tmp)

    def display(self):
        self.displayConcepts()
        self.displayVerbalizedConcepts()
        self.displayInstances()
        self.view.draw()

    def displayVerbalizedConcepts(self):
        text = '\n'.join([verbalizeConcept(c) for c in self.conceptList])
        self.view.node(text, apply_template(Verbalized_Template, text))


class Obj(object):
    def __init__(self, **kwargs):
        for key,val in kwargs.items():
            setattr(self, key, val)

def view(obj, kls):
    return view1(obj, kls, {})


# only supports traits that are primitive and Instance(X)
def view1(objA, concept_class, views):  # , mapping)
    ## Answers: can <objA> be correctly viewed as a <concept_class>?
    ## returns instance of <concept_class> with _errs_ attribute
    ## _errs_ = [] means the match is valid; otherwise, _errs_ = explanation
    ## <views> is a dictionary of {(objA, concept_class) :  mapped_instance }
    ##   this is used to prevent infinite loops due to cycles between objects
    if (objA, concept_class) in views:
        return views[(objA, concept_class)]
    if not issubclass(concept_class, Concept):
        if isinstance(objA, concept_class):
            return objA
        else:
            objA._errs_ = [("self", "Not instance of %s" % concept_class)]
            return objA
    if issubclass(concept_class, Concept):
        if isinstance(objA, concept_class):
            objB = objA
            objB._errs_ = []
        else:
            objB = concept_class()
            objB._errs_ = []
            traits = classTraits(concept_class)
            for name, trait in traits.items():
                try:
                    valA = getattr(objA, name) if hasattr(objA, name) else None
                    if valA:
                        if isPrimitive(trait):
                            valB = valA
                        elif isInstanceTrait(trait):
                            v2 = dict(views)
                            v2.update({(objA, concept_class): objB})
                            valB = view1(valA, trait.trait_type.klass, v2)
                            if valB._errs_: objB._errs_.append((name, 'invalid %s' % concept_class))
                        else: raise Exception("Unsupported Trait Type")
                        trait.validate(objB, name, valB)
                        setattr(objB, name, valB)
                except Exception as err:
                    objB._errs_.append((name, "%s" % err))
            # TODO: carry over non-trait attributes from objA to objB
            # e.g. for list of values of functions pos=[(t1,p1), (t2,p2)...]

        # @rules checks
        for m_name, meth in getRules(concept_class):
            def fail():
                objB._errs_.append((m_name, meth.__doc__ or "@rule failed"))
            try:
                ok = meth(objB)
                if not ok: fail()
            except Exception:
                fail()

        return objB


import inflect
english = inflect.engine()


def verbalizeConcept(concept):
    name_and_doc = "%s: %s " % (concept.__name__, concept.__doc__ or "")
    every_one_has = "Every %s" % concept.__name__ + \
                    (' is a %s, and' % concept.__bases__[0].__name__ \
                         if (concept.__bases__ != (object,) and concept.__bases__ != (Concept,)) \
                         else '') + \
                    ' has attributes:\n\t'
    traits = classTraits(concept)
    attrs = '\n\t'.join(["%s, which is %s" % (n, english.a(verbalize(tr))) for n, tr in traits.items()])

    rules = getRules(concept)
    rulesTxt = ('\n    and has rules:\n\t' + '\n\t'.join([rName for rName, f in rules])) if rules else ''

    return name_and_doc + every_one_has + attrs + rulesTxt


def graph_file(obj, func_name, param, range, highlights):
    ## plots the named function on obj, taking param over its range (start, end)
    ## highlights are pairs of (x_value, "Text_to_show") to annotate on the graph plot
    ## saves the plot to a file and returns full file name

    import numpy, pylab

    func = getattr(obj, func_name)
    f = numpy.vectorize(func)
    x = numpy.linspace(*range)
    y = f(x)
    pylab.rc('font', family='serif', size=20)
    pylab.plot(x, y)
    pylab.xlabel(param)
    pylab.ylabel(func_name)
    hi_pts = [pt for pt, txt in highlights]
    pylab.plot(hi_pts, f(hi_pts), 'rD')
    for pt, txt in highlights:
        pt_y = func(pt)
        ann = txt + "\n(%s,%s)" % (pt, pt_y)
        pylab.annotate(ann, xy=(pt, pt_y))

    import os, time

    file = os.path.dirname(__file__) + "/generated_graphs/%s.%s.%s.pdf" % (type(obj).__name__, func_name, time.time())
    pylab.savefig(file, dpi=300)
    pylab.close()
    return file
