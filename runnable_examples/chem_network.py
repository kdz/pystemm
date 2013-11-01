from chem_balance import *


class Network(Concept):
    reactions = List(Instance(Reaction))
    class_template = {K.fill_color: 'Red'}
    instance_template = {K.name: 'AdjustableDoubleArrow'}


CO = Molecule(formula=[(E('C'), 1),
                       (E('O'), 1)])

NO2 = Molecule(formula=[(E('N'), 1),
                        (E('O'), 2)])

NO3 = Molecule(formula=[(E('N'), 1),
                        (E('O'), 3)])

CO2 = Molecule(formula=[(E('C'), 1),
                        (E('O'), 2)])

NO = Molecule(formula=[(E('N'), 1),
                       (E('O'), 1)])

R1 = Reaction(reactants=[(2, NO2)],
              products=[(1, NO3), (1, NO)])

R2 = Reaction(reactants=[(1, NO3), (1, CO)],
              products=[(1, NO2), (1, CO2)])

Net = Network(reactions=[R1, R2])

m = Model(Network, Reaction, Molecule, Element)
# m.attrFilter({Reaction: ['ins', 'outs'],
#               Molecule: []})
m.addInstances(Net, R1, R2, NO2, NO3, NO, CO)

m.display()