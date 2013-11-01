from model import *

class A(Concept):
    i = Int
    s = String
    class_template = {K.text: [{K.color: 'Red'},
                               {K.color: 'Green'}]}

M = Model(A)
M.display()

