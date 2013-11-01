from model import *

class Element(Concept):
    name = String
    class_template = {K.fill_color: 'Asparagus'}
    instance_template = {K.name: 'Circle'}
    def label(self):
        return self.name

class Molecule(Concept):
    formula = List(Tuple(Instance(Element), Int))
    class_template = {K.fill_color: 'Blue'}
    instance_template = {K.side_padding: 0, K.vertical_padding: 20}
    def label(self):
        return ''.join( [el.label() +
                         (str(i) if i > 1 else '')
                         for el,i in self.formula] )

class Reaction(Concept):
    products = List(Tuple(Int, Instance(Molecule)))
    reactants = List(Tuple(Int, Instance(Molecule)))
    class_template = {K.fill_color: 'Red'}
    instance_template = {K.side_padding: 0, K.vertical_padding: 20, K.name: 'AdjustableArrow'}

    def label(self):
        return ' + '.join( [(str(i) if i > 1 else '') + m.label() for i,m in self.reactants]) + \
               '\n -> \n' + \
               ' + '.join( [(str(i) if i > 1 else '') + m.label() for i,m in self.products])


def E(name): return Element(name=name)

KNO3 = Molecule(formula = [
    (E('K'),1),
    (E('N'), 1),
    (E('O'), 3)])

C1 = Molecule(formula=
[(E('C'),1)])

K2CO3 = Molecule(formula=
[(E('K'),2),
 (E('C'),1),
 (E('O'),3)])

CO = Molecule(formula=
[(E('C'),1),
 (E('O'),1)])

N2 = Molecule(formula=
[(E('N'),2)])

R = Reaction(
    reactants = [(2, KNO3), (4, C1)],
    products = [(1, K2CO3), (3, CO), (1, N2)] )

M = Model(Reaction, Molecule, Element)

M.addInstances(R)

#M.showMethod(KNO3, 'label')

M.view.layout(Hierarchical_Layout_Props)

M.display()