from model import *
from func1 import *

class InverseFunction(Function):
    inverts = Instance(Function)
    domain = Property(List(Int))

    @cached_property
    def _get_domain(self):
        return [self.inverts.eval(x)
                for x in self.inverts.domain]

    def eval(self, y):
        return find(x1 for x1 in self.inverts.domain
                       if y==self.inverts.eval(x1))

    class_template = {K.gradient_color: 'Blue'}

def inverse(f):
    return InverseFunction(inverts=f)

inv = inverse(tf)

M.addClasses(InverseFunction)
M.addInstances(inv)
M.showMethod(inv, 'eval')
M.showEval(inv, 'eval',[10])

if __name__=='__main__':
    M.display()
