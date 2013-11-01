from model import *

class A(Concept):
    i = Int
    f = Float

M = Model(A)

def test_emptyAttrFilter():
    assert M._attrPassesFilter(A, 'i')
    assert M._attrPassesFilter(A, 'f')

def test_blockedAttrFilter():
    M.attrFilter({A: ['i']})
    assert M._attrPassesFilter(A, 'i')
    assert not M._attrPassesFilter(A, 'f')
