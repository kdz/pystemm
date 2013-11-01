from model import *

class Factorial(Concept):
    n = Int
    value = Int

    def eval(self):
        if self.n <= 1:
            self.value = 1
        else:
            self.recur = Factorial(n = self.n - 1)
            self.value = self.n * self.recur.eval()
        return self.value

    def label(self):
        return "fact(%s)=%s%s" % (self.n, self.n, '' if self.value==1 else '*...')

Factorial.add_class_trait('recur',Instance(Factorial))

M = Model(Factorial)

f = Factorial(n=4)
f.eval()

M.addInstances(f)

M.display()