from model import *


class A(Concept):
    def x(self, t): return 20 * t

    def y(self, t): return 10 * t * t


a = A()
M = Model(A)
M.addInstances(a)

M.animate(a, (0, 10), 10,
          [{K.new: K.shape, K.origin: lambda o, t: [o.x(t), o.y(t)], K.name: 'Circle', K.fill_color: "Black",
            K.size: [10, 10]},
           {K.new: K.shape, K.origin: lambda o, t: [o.x(t) + 20, o.y(t)], K.name: 'Circle', K.fill_color: "Red",
            K.size: [10, 10]},
           {K.new: K.line, K.point_list: lambda o, t: [[o.x(t), o.y(t)], [o.x(t) + 16, o.y(t)]]}])

