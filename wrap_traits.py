## This module provides utility functions around the Enthought "traits" module
## Other parts of PySTEMM use these utility functions

import traits.api as TR

## A bunch of Boolean functions for specific trait combinations

def isPrimitive(cTrait):
    return isinstance(cTrait.trait_type, (TR.Int, TR.String, TR.Bool, TR.Float))#, TR.Callable))

def isInstanceTrait(cTrait):
    return isinstance(cTrait.trait_type, TR.Instance)

def isCallableTrait(cTrait):
    return isinstance(cTrait.trait_type, TR.Callable)

def isListOfInstanceTrait(cTrait):
    return isinstance(cTrait.trait_type, TR.List) \
        and isinstance(cTrait.trait_type.item_trait.trait_type, TR.Instance)

def isListOfTupleOfInstancePrim(cTrait):
    return isinstance(cTrait.trait_type, TR.List) and\
           isinstance(cTrait.trait_type.item_trait.trait_type, TR.Tuple) and\
           isPrimitive(cTrait.trait_type.item_trait.trait_type.types[1]) and\
           isInstanceTrait(cTrait.trait_type.item_trait.trait_type.types[0])

def isListOfTupleOfPrimInstance(cTrait):
    return isinstance(cTrait.trait_type, TR.List) and\
           isinstance(cTrait.trait_type.item_trait.trait_type, TR.Tuple) and\
           isPrimitive(cTrait.trait_type.item_trait.trait_type.types[0]) and\
           isInstanceTrait(cTrait.trait_type.item_trait.trait_type.types[1])

def isListOfPrim(cTrait):
    return isinstance(cTrait.trait_type, TR.List) and \
           isPrimitive(cTrait.trait_type.item_trait)

def isTupleOfPrim(cTrait):
    return isinstance(cTrait.trait_type, TR.Tuple) and \
        all(isPrimitive(x) for x in cTrait.trait_type.types)

def isListOfTupleOfPrim(cTrait):
    return isinstance(cTrait.trait_type, TR.List) and \
           isTupleOfPrim(cTrait.trait_type.item_trait)

def compressedTraitName(t):
    ## makes useful short names from complex trait structure (cTrait, item_trait, trait_type, ... etc.)
    ## e.g. "(Int, Int)" for Tuple(Int, Int)
    ## ... and "List(Int)" for List(Int)

    if isinstance(t, TR.Tuple):
        return "(" + \
               ','.join([cT.trait_type.__class__.__name__ for cT in t.types]) + \
               ")"
    if isinstance(t, TR.List):
        return compressedTraitName(t.item_trait.trait_type)
    return t.__class__.__name__

def verbalize(cTraitOrKls):
    ## a narrative string for the type of the trait e.g. "list of ..."
    typ = type(cTraitOrKls)
    if typ == TR.CTrait:
        if isPrimitive(cTraitOrKls):
            return cTraitOrKls.trait_type.__class__.__name__
        if isInstanceTrait(cTraitOrKls):
            return cTraitOrKls.trait_type.klass.__name__
        if isListOfInstanceTrait(cTraitOrKls):
            return "list of " + cTraitOrKls.trait_type.item_trait.trait_type.klass.__name__ + "s"
        if isListOfTupleOfPrimInstance(cTraitOrKls) or \
                isListOfTupleOfInstancePrim(cTraitOrKls) or \
                isListOfTupleOfPrim(cTraitOrKls):
            return "list of pairs of " + \
                   verbalize(cTraitOrKls.trait_type.item_trait.trait_type.types[0]) + \
                   " and " + \
                   verbalize(cTraitOrKls.trait_type.item_trait.trait_type.types[1])
        if isListOfPrim(cTraitOrKls):
            return "list of " + verbalize(cTraitOrKls.trait_type.item_trait) + "s"
        else: return cTraitOrKls.trait_type.__class__.__name__
    else:
        return cTraitOrKls.__class__.__name__

class Attr(object):
    ## Represents an attribute DEFINITION on a class

    def __init__(self, n, cT):
        ## simply stores the attribute name, and the cTrait
        self.name = n
        self.type = cT

def classTraits(cls):
    # returns dict excluding trait_added and trait_modified (2 built-in's of the traits module itself)

    if isinstance(cls, TR.MetaHasTraits):
        return { key:val for key, val in cls.class_traits().items() if key not in ('trait_added', 'trait_modified')}
    else:
        return {}

def endPoint(cTrait):
    # return end-point class for drawing a line
    # e.g. Reaction:: inputs = List(Instance(Molecule)):
    # .... the end point for drawing "inputs" line is Molecule, not List of Instance

    if isInstanceTrait(cTrait):
        return cTrait.trait_type.klass

    if isListOfInstanceTrait(cTrait):
        return cTrait.trait_type.item_trait.trait_type.klass

    if isListOfTupleOfInstancePrim(cTrait):
        return cTrait.trait_type.item_trait.trait_type.types[0].trait_type.klass

    if isListOfTupleOfPrimInstance(cTrait):
        return cTrait.trait_type.item_trait.trait_type.types[1].trait_type.klass

    if isListOfPrim(cTrait):
        return cTrait.trait_type.item_trait.trait_type

    if isListOfTupleOfPrim(cTrait):
        return cTrait.trait_type.item_trait.trait_type

    if isinstance(cTrait.trait_type, TR.Callable):
        return TR.Callable

    return cTrait.trait_type

    raise Exception