from model import *
import pylpsolve

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
        return ''.join([el.label() +
                        (str(i) if i > 1 else '')
                        for el, i in self.formula])

    def atom_count(self, atom_name):
        l = [i for (atom, i) in self.formula if atom.name == atom_name]
        return l[0] if l else 0


class Reaction(Concept):
    ins = List(Instance(Molecule))
    outs = List(Instance(Molecule))

    class_template = {K.fill_color: 'Red'}
    instance_template = {K.side_padding: 0, K.vertical_padding: 20, K.text: '', K.name: 'AdjustableArrow'}

    def label(self):
        return ' + '.join(['?' + m.label() for m in self.ins]) + \
               '\n -> \n' + \
               ' + '.join(['?' + m.label() for m in self.outs])

    def element_names(self):
        names = []
        for m in self.ins + self.outs:
            for (atom, j) in m.formula:
                if atom.name not in names: names.append(atom.name)
        return names

    def molecule_names(self):
        return [m.label() for m in self.ins + self.outs]

    def signed_molecules(self):
        return [(1, m) for m in self.ins] + [(-1, m) for m in self.outs]

    def elem_balance_matrix(self):
        matrix = []
        for elem_name in self.element_names():
            row = []
            for (molec_sign, molec) in self.signed_molecules():
                row.append(molec_sign * molec.atom_count(elem_name))
            matrix.append(row)
        return matrix

    def number_of_molecules(self):
        return len(self.ins) + len(self.outs)

    def diagonal_matrix(self):
        matrix = []
        for i in range(self.number_of_molecules()):
            row = [(1 if j == i else 0) for j in range(self.number_of_molecules())]
            matrix.append(row)
        return matrix

    def objective_function(self):
        return self.diagonal_matrix()[0]

    def balance(self):
        lp = pylpsolve.LP()
        lp.addConstraint(self.elem_balance_matrix(), "=", 0)
        lp.addConstraint(self.diagonal_matrix(), ">=", 1)
        lp.setInteger((0, self.number_of_molecules() - 1))
        lp.setObjective(self.objective_function(), mode="minimize")
        lp.solve()
        return lp.getSolution()


def E(name):
    return Element(name=name)


KNO3 = Molecule(formula=[(E('K'), 1),
                         (E('N'), 1),
                         (E('O'), 3)])

C1 = Molecule(formula=[(E('C'), 1)])

K2CO3 = Molecule(formula=[(E('K'), 2),
                          (E('C'), 1),
                          (E('O'), 3)])

CO = Molecule(formula=[(E('C'), 1),
                       (E('O'), 1)])

N2 = Molecule(formula=[(E('N'), 2)])

R = Reaction(ins=[KNO3, C1], outs=[K2CO3, CO, N2])

M = Model(Reaction, Molecule)
M.attrFilter({Molecule: []})
M.addInstances(R)

M.showMethod(R, 'balance')

# ###### some custom display functions for reaction R
from prettytable import PrettyTable

def format_elem_matrix(matrix):
    els = R.element_names()
    mols = R.molecule_names()
    table = PrettyTable(field_names=[''] + mols)
    for i, e in enumerate(els):
        table.add_row([e] + matrix[i])
    return str(table)

def format_balance(coeffs):
    coeffs = [int(x) for x in coeffs]
    mols = R.molecule_names()
    table = PrettyTable(field_names=mols)
    table.add_row(coeffs)
    return str(table)

def format_diag_matrix(matrix):
    mols = R.molecule_names()
    table = PrettyTable(field_names=mols)
    for row in matrix: table.add_row(row)
    return str(table)

if __name__ == '__main__':
    # ###### display the pylpsolve matrices & result of balancing

    M.showEval(R, 'elem_balance_matrix', [], {K.text: {K.text: format_elem_matrix,
                                                       K.font: "CourierNewPS-BoldMT" }})
    M.showEval(R, 'diagonal_matrix', [], {K.text: {K.text: format_diag_matrix,
                                                   K.font: "CourierNewPS-BoldMT"}})
    M.showEval(R, 'objective_function', [])
    M.showEval(R, 'balance', [], {K.text: {K.text: format_balance,
                                           K.font: "CourierNewPS-BoldMT"}})

    M.view.layout(Hierarchical_Layout_Props)

    M.display()

