from model import *

class Function(Concept):
    """Give an x value and eval() it."""
    def eval(self, x):
        pass

class RuleFunc(Function):
    """The eval() rule is defined by a Python expression"""
    rule = TR.Callable
    class_template = {K.fill_color: 'Asparagus'}
    def eval(self, x):
        return self.rule(x)

class Transform(Function):
    source = Instance(Function)
    pass

class ShiftX(Transform):
    """A function whose value is the x-shifted value of another."""
    by = Int
    class_template = {K.fill_color: 'Red'}

    def label(self): return "ShiftX\nby: " + str(self.by)

    def eval(self, x):
        return self.source.eval(x + self.by)

class Bump(Transform):
    """A function whose value is the same as another, except for a flat 'bump'."""
    start = Int
    end = Int
    val = Int
    def label(self):
        return "Bump\nstart:%s\nend:%s\nval:%s" % (self.start, self.end, self.val)
    def eval(self, x):
        if x < self.start or x > self.end:
            return self.source.eval(x)
        else:
            return self.val
    class_template = {K.fill_color: 'Blue'}

def square(x):
    return x ** 2

t = RuleFunc(rule=square)

s = ShiftX(source=t, by=3)

u = Bump(source=s, start=0, end=5, val=100)

m = Model(ShiftX, Function, Transform, RuleFunc, Bump)
m.addInstances(s, t, u)

for x in [s,t,u]:
    m.showGraph(x,'eval','x',(-10,10))

m.showMethod(s,'eval')
m.showMethod(u,'eval')
#im.show_function_value(s,'eval',5)
#im.show_function_value(t,'eval',5)
m.display()