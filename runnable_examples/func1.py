from model import *

class Function(Concept):
    domain = Property(List(Int))

    def eval(self, x):
        pass

    class_template = {K.gradient_color: 'Green'}

class TableFunction(Function):
    points = List(Tuple(Int, Int))
    domain = Property(List(Int))

    @cached_property
    def _get_domain(self):
        return [x for x, y in self.points]

    def eval(self, x):
        return find(y1 for x1,y1 in self.points
                       if x1==x)

    class_template = {K.gradient_color: 'Maroon'}
    instance_template = {K.name: 'Circle'}

class RuleFunction(Function):
    rule = TR.Callable
    domain = List(Int)

    def eval(self, x):
        return self.rule(x)

    class_template = {K.gradient_color: 'Yellow'}

tf = TableFunction(points=[(1, 10), (2, 15)])

rf = RuleFunction( domain=[1, 2], rule= \
    lambda x: x ** 2 + 2
)

M = Model(Function,TableFunction,RuleFunction)

M.addInstances(tf) #rf)

#M.showMethod(rf, 'eval')
M.showMethod(tf, 'eval')
#M.showMethod(tf, '_get_domain')
#M.showEval(rf,'eval',[2])
M.showEval(tf,'eval',[1])

if __name__=='__main__':
    M.display()
