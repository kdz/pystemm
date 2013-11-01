## This module defines:
##      Templates: dicts of OmniGraffle properties, including deferred functions
##      Functions to merge templates together, and to apply a template to a Concept, Instance, etc.
##      Utility functions to calculate display names and text for concepts, instances, & lines

import appscript
from wrap_traits import *

K = appscript.k


class TextDict(object):
    ## This is currently NOT used ... should perhaps just remove?
    def __init__(self, order, **kwargs):
        self.order = order
        self.dict = kwargs

    def toOG(self):
        extras = list(set(self.dict.keys()).difference(set(self.order or [])))
        return [{K.text: self.dict[key]} for key in self.order + extras
                if key in self.dict]

## Template vs. Props: one is ready to be passed directly to OmniGraffle (OG), not the other
## XYZ_Template: contains some Callables,
##      ... so has to be "applied" to convert functions to specific OG property valuesOG
## XYZ_Props: does not contain Callables, can be passed direct to OG

Concept_Template = {K.text: lambda concept: classLabel(concept),
                    K.name: 'Rectangle',
                    K.corner_radius: 6,
                    K.side_padding: 7,
                    K.vertical_padding: 6,
                    K.text_placement: K.top,
                    K.autosizing: K.full,
                    K.draws_shadow: True,
                    K.stroke_color: 'Black',
                    K.blend_fraction: 0.6,
                    K.fill: K.linear_fill,
                    K.fill_color: "Snow",
                    K.gradient_angle: 45.0,
                    K.gradient_color: "Snow"}

Verbalized_Template = {K.text: lambda text: text,
                       K.name: 'Rectangle',
                       K.corner_radius: 0,
                       K.side_padding: 7,
                       K.vertical_padding: 6,
                       K.text_placement: K.top,
                       K.alignment: K.left,
                       K.autosizing: K.full,
                       K.draws_shadow: False,
                       K.stroke_color: 'Black',
                       #k.fill: k.solid,
                       K.fill_color: "Snow"}

Instance_Template = {K.stencil_name: 'Instance',
                     K.corner_radius: 0,
                     K.vertical_padding: 0,
                     K.side_padding: 20,
                     K.draws_shadow: False,
                     K.text: lambda obj: instLabel(obj)}

Rel_Template = {
    K.head_type:
        lambda attr: "StickArrow" \
            if isPrimitive(attr.type) or isInstanceTrait(attr.type) or isCallableTrait(attr.type) \
            else "DoubleStickArrow",
    K.line_type: K.straight
}

Subclass_Props = {K.head_scale: 1.3,
                  K.double_stroke: True,
                  K.stroke_cap: K.butt,
                  K.thickness: 4,
                  K.head_type: u'FilledArrow'}

Link_Props = {
    K.head_type: "StickArrow",
    K.line_type: K.straight
}

Val_Template = {K.text: lambda val: '%s' % val,
                K.autosizing: K.full,
                K.draws_stroke: False,
                K.draws_shadow: False}

Graph_Template = {K.size: [300, 220],
                  K.text: K.missing_value,
                  K.draws_stroke: True,
                  K.stroke_color: [0.8, 0.8, 0.8],
                  K.draws_shadow: True,
                  K.autosizing: K.overflow,
                  K.image: lambda file: file,
                  # k.image_scale: 0.5
                  K.image_sizing: K.manual}

import textwrap
import inspect

## This template is to display source code of a method or "lambda" function
## uses the "inspect" module to get source code
Callable_Template = {K.text:
                         {K.text: lambda meth: textwrap.dedent(inspect.getsource(meth).replace("    ","  ")),
                          K.font: 'LucidaConsole'},
                     K.autosizing: K.full,
                     K.stroke_color: 'Aluminum',
                     K.name: 'DocumentShape'}


def relationLabel(attr):
    ## the string label for the line joining 2 Concept Classes
    if isListOfTupleOfInstancePrim(attr.type):
        t1 = attr.type.trait_type.item_trait.trait_type.types[0].trait_type.klass.__name__
        t2 = type(attr.type.trait_type.item_trait.trait_type.types[1].trait_type).__name__
        return attr.name + "\n" + ('(%s,%s)' % (t1, t2) )
    elif isListOfTupleOfPrimInstance(attr.type):
        t2 = attr.type.trait_type.item_trait.trait_type.types[1].trait_type.klass.__name__
        t1 = type(attr.type.trait_type.item_trait.trait_type.types[0].trait_type).__name__
        return attr.name + "\n" + ('(%s,%s)' % (t1, t2) )
    else:
        return attr.name


Rel_Label_Template = {
    K.text: relationLabel,
    K.fill: K.linear_fill,
    K.fill_color: 'Snow',
    K.gradient_color: "Snow"
}


def lineLabel(str):
    return dict(Rel_Label_Template.items() + {K.text: str}.items())


def mergeTemplates(t1, t2):
    # takes templates t1, t2; returns merged template, favoring t1 where they overlap
    # recursively merges any dicts and lists
    if t1 is None:
        return t2
    if t2 is None:
        return t1
    if isinstance(t1, list) and isinstance(t2, list):
        return [mergeTemplates(x, y) for x, y in map(None, t1, t2)]
    if isinstance(t1, TextDict) and isinstance(t2, TextDict):
        return TextDict(mergeTemplates(t1.order, t2.order),
                        **mergeTemplates(t1.dict, t2.dict))
    if isinstance(t1, dict) and isinstance(t2, dict):
        keys = set(t1.iterkeys()) | set(t2.iterkeys())
        return {key: mergeTemplates(t1.get(key), t2.get(key)) for key in keys}
    if callable(t1) or callable(t2):
        return lambda obj: mergeTemplates(apply_template(t1, obj), apply_template(t2, obj))
    return t1


def apply_template(t, obj, time=None):
    # template: a dictionary, keys are OG keys, values are OG values or functions
    # obj: any kind of object, which can be passed into the template functions
    # time: an optional parameter, to allow animation template with functions(obj,time)
    # returns: a copy of template with all functions F replaced F(obj)"""

    if isinstance(t, dict):
        return {k: apply_template(v, obj, time) for k, v in t.items()}
    if isinstance(t, list):
        return [apply_template(x, obj, time) for x in t]
    if isinstance(t, TextDict):
        return apply_template(t.toOG(), obj, time)
    if callable(t):
        ## check if callable has 1 arg or 2 args, call with (obj) or (obj,time) accordingly
        arity = len(inspect.getargspec(t).args) if inspect.ismethod(t) or inspect.isfunction(t) else 1
        if arity == 1:
            return t(obj)
        else:
            return t(obj, time)
    return t


def netClassTemplate(cls):
    ## merge any template specific to cls, with the default Concept_Template

    return mergeTemplates(cls.class_template if hasattr(cls, 'class_template') else {},
                          Concept_Template)


def netInstanceTemplate(obj):
    ## merge any instance_template on obj's class, with the netClassTemplate

    kls = type(obj)
    inst_template = kls.instance_template if hasattr(kls, 'instance_template') else {}
    return mergeTemplates(inst_template,
                          mergeTemplates(Instance_Template, netClassTemplate(kls)))


def rule(method):
    ## use for @rule decorator
    method.is_rule = True
    return method


def getRules(cls):
    ## return list of methods that were marked with @rule
    if not inspect.isclass(cls):
        return []
    else:
        methods = inspect.getmembers(cls, predicate=inspect.ismethod)
        return [(name, meth) for name, meth in methods if hasattr(meth, 'is_rule')]


def classLabel(cls_or_trait):
    ## return class_name + text_attributes to show inside the box
    ## using different fonts & alignment for name vs. attributes

    clsName = cls_or_trait.__name__ if hasattr(cls_or_trait, '__name__') \
        else compressedTraitName(cls_or_trait)
    attrString = '\n'.join([attr + ': ' + type(val.trait_type).__name__ \
                            for attr, val in classTraits(cls_or_trait).items() if isPrimitive(val)])
    rules = getRules(cls_or_trait)
    ruleNames = '\n'.join([name for name, meth in rules])
    rulesStrings = [{K.text: '\nrules', K.font: "Helvetica-Bold", K.alignment: K.center},
                    {K.text: '\n' + ruleNames, K.font: "Helvetica-Oblique", K.alignment: K.left}] if rules else []
    return [{K.text: clsName, K.font: "Helvetica-Bold", K.alignment: K.center}] + \
           ([{K.text: '\n' + attrString, K.font: "Helvetica", K.alignment: K.left}] if attrString else []) + \
           rulesStrings


def instLabel(obj):
    ## returns text label for an instance

    ## if it has a "label" method, just use that
    if hasattr(obj, 'label'):
        return obj.label()

    ## if it is an (indirect) instance of TR.HasTraits, gather all isPrimitive attribute values
    if isinstance(obj, TR.HasTraits):
        traits = classTraits(type(obj))
        attrList = ["%s=%s" % (k, getattr(obj, k)) for k, v in traits.items() if isPrimitive(v)]
        return '\n'.join(attrList)

    ## otherwise just use default Python string representation e.g. "[1, 2]" for a list with 1, 2
    else:
        return "%s" % obj

# ########

if __name__ == '__main__':
    pass