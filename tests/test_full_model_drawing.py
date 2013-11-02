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
    mix = TR.List(TR.Tuple(TR.Instance(Organelle), TR.Int))
    func = TR.Callable
    f2 = TR.Callable

    ll = TR.List(TR.Tuple(TR.Int, TR.Int))

    class_template = {K.fill_color: 'Blue'}

    @rule
    def foo(self, x, y): return x + y

    @rule
    def bar(self): pass

# used because of undefined references
Membrane.add_class_trait('surrounds', TR.Instance(Cell))

m = Model(Cell, Membrane, Organelle)

o1, o2 = Organelle(), Organelle()

cell = Cell(kind='plant',
            size=100,
            membrane=Membrane(thickness=20),
            organelles=[o1, o2],
            mix = [(o1, 2), (o2, 9)],
            func=lambda x: x ** 3,
            f2 = lambda x: x ** 2,
            ll=[(2, 3), (4, 5)])

m.addInstances(cell)

m.showMethod(cell, 'foo')

m.showEval(cell, 'func', [3])

m.showEval(cell, 'foo', [3, 4], {K.text: lambda x: "RESULT=%s" % x, K.autosizing: K.full})

m.showGraph(cell, ['func','f2'], 'x', (-3, 3))

m.display()

