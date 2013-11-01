from model import *

class Organelle(Concept):
    class_template = {K.fill_color: 'Orange'}

class Membrane(Concept):
    thickness = TR.Int
    class_template = {K.fill_color: 'Teal'}

class Cell(Concept):
    kind = TR.String
    isAlive = TR.Bool
    size = TR.Int
    organelles = TR.List(TR.Instance(Organelle))
    membrane = TR.Instance(Membrane)
    m2 = TR.List(Membrane)
    mix = TR.List(TR.Tuple(TR.Instance(Organelle), TR.Int))
    func = TR.Callable
    intList = List(Int)
    intTupleList = List(Tuple(Int,Int))
    ll = TR.List(TR.Tuple(TR.Int, TR.Int))
    class_template = {K.fill_color: 'Blue'}
    def foo(self, x, y): return x + y

Membrane.add_class_trait('surrounds', TR.Instance(Cell))

Cell_traits = Cell.class_traits()

# ############### TESTS ###############

def test_wrap_traits():
    assert classTraits(Organelle) == {}

    assert isInstanceTrait(Cell_traits['membrane'])
    assert not isInstanceTrait(Cell_traits['kind'])

    assert isListOfInstanceTrait(Cell_traits['organelles'])
    assert not isListOfInstanceTrait(Cell_traits['mix'])

    assert isListOfTupleOfInstancePrim(Cell_traits['mix'])
    assert not isListOfTupleOfInstancePrim(Cell_traits['size'])

    assert isListOfPrim(Cell_traits['intList'])
    assert not isListOfPrim(Cell_traits['organelles'])
    assert isListOfTupleOfPrim(Cell_traits['ll'])

    assert endPoint(Cell_traits['membrane']) == Membrane
    assert endPoint(Cell_traits['organelles']) == Organelle
    assert endPoint(Cell_traits['mix']) == Organelle
    assert endPoint(Cell_traits['intList']).__class__ == TR.Int
    assert endPoint(Cell_traits['ll']).__class__ == TR.Tuple

    assert compressedTraitName(endPoint(Cell_traits['intList'])) == 'Int'
    assert compressedTraitName(endPoint(Cell_traits['ll'])) == '(Int,Int)'

def test_templates_and_labels():
    assert relationLabel(Attr('mix', Cell_traits['mix'])) == 'mix\n(Organelle,Int)'

    assert apply_template(Rel_Template, Attr('membrane', Cell_traits['membrane'])) == {K.head_type: "StickArrow",
                                                                                       K.line_type: K.straight}

    assert apply_template(Rel_Template, Attr('organelles', Cell_traits['organelles'])) == {K.head_type: "DoubleStickArrow",
                                                                                           K.line_type: K.straight}

    assert instLabel(Membrane(thickness=3)) == 'thickness=3'


def test_compressed_trait_name():
    assert compressedTraitName(endPoint(Cell_traits['intList'])) == 'Int'
    assert compressedTraitName(endPoint(Cell_traits['size'])) == 'Int'
    assert compressedTraitName(endPoint(Cell_traits['intTupleList'])) == '(Int,Int)'

def test_verbalize():
    assert verbalize(Cell_traits['kind']) == 'String'
    assert verbalize(Cell_traits['isAlive']) == 'Bool'
    assert verbalize(Cell_traits['organelles']) == 'list of Organelles'
    assert verbalize(Cell_traits['membrane']) == 'Membrane'
    assert verbalize(Cell_traits['mix']) == 'list of pairs of Organelle and Int'
    assert verbalize(Cell_traits['func']) == 'Callable'
    assert verbalize(Cell_traits['intList']) == 'list of Ints'
    assert verbalize(Cell_traits['intTupleList']) == 'list of pairs of Int and Int'
