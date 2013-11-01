from model import *


class B(Concept):
    s = String
    @rule
    def s_not_errorString(self): return self.s != "error"

class A(Concept):
    i = Int
    b = Instance(B, allow_none=True)
    @rule
    def i_LT_5(self): return self.i < 5

B.add_class_trait('a',Instance(A))

def num_of_view_errors(v):
    return len(v._errs_)

def test_view_primitives():
    assert not num_of_view_errors(view(Obj(i=2), A))
    assert num_of_view_errors(view(Obj(i="bob"), A))==1

def test_view_rules():
    assert num_of_view_errors(view(Obj(i=9),A))==1
    assert num_of_view_errors(view(Obj(s="error"), B))==1

def test_view_instance():
    assert not num_of_view_errors(view(Obj(b=B(s="s")),
                               A))
    assert not num_of_view_errors(view(Obj(i=2,b=Obj(s="s")),
                                A))
    v = view(Obj(i=9, b=Obj(s=A())), A)
    assert num_of_view_errors(v) == 2

def test_cycles_view_ok():
    ao = Obj()
    bo = Obj(a = ao)
    ao.b = bo
    assert not num_of_view_errors(view(ao, A))

def test_cycles_view_failure():
    ao = Obj()
    bo = Obj(a = ao, s="error")
    ao.b = bo
    assert num_of_view_errors(view(ao, A)) == 1

def test_unsupported_traits():
    class C(Concept): bs = List(Tuple(Int,Instance(A)))

    assert num_of_view_errors(view(Obj(bs=2),C))