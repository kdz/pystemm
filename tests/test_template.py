from template import *


def test_merge_dicts():
    assert mergeTemplates({}, {}) == {}
    assert mergeTemplates({'a': 1, 'b': 2}, {'b': 5, 'c': 3}) == {'a': 1, 'b': 2, 'c': 3}
    assert apply_template({'a': 1, 'b': lambda x: x + 2}, 9) == {'a': 1, 'b': 11}


def test_merge_lists():
    assert mergeTemplates([1, 2], [1, 9, 3]) == [1, 2, 3]
    assert mergeTemplates([{1: 'a'}], [{2: 'b'}, 'c']) == [{1: 'a', 2: 'b'}, 'c']


def test_merge_text_dicts():
    t1 = TextDict(['head', 'body', 'tail'],
                  head={K.text: 'head'},
                  body={K.text: 'body'},
                  tail={K.text: 'tail'})
    t2 = TextDict(None,
                  head={K.text: 'head Lost'},
                  body={K.font: 'Helvetica-Bold'},
                  tail={K.alignment: K.left},
                  ps="ps")
    assert t1.toOG() == [{K.text: {K.text: 'head'}},
                         {K.text: {K.text: 'body'}},
                         {K.text: {K.text: 'tail'}}]
    merged = mergeTemplates(t1, t2)
    assert merged.order == ['head', 'body', 'tail']
    assert merged.toOG() == [
        {K.text: {K.text: 'head'}},
        {K.text: {K.text: 'body', K.font: 'Helvetica-Bold'}},
        {K.text: {K.text: 'tail', K.alignment: K.left}},
        {K.text: "ps"}
    ]


def test_apply_template():
    obj = "abc"
    assert apply_template({1: len}, obj) == {1: 3}
    assert apply_template({1: [len, str]}, obj) == {1: [3, "abc"]}
    assert apply_template("bob", obj) == "bob"
    assert apply_template([1, 2], obj) == [1, 2]
    assert apply_template(TextDict(['head', 'body'],
                                   head=len,
                                   body=str), obj) == [{K.text: 3},
                                                       {K.text: "abc"}]

def test_deferred_merge():
    m1 = mergeTemplates({1:len}, {1: "bob"})
    assert callable(m1[1])
    assert apply_template(m1,"abc") == {1: 3}

    m2 = mergeTemplates({1:len}, {2: str, 3: "three"})
    assert callable(m2[1]) and callable(m2[2]) and not callable(m2[3])
    assert apply_template(m2, "abc") == {1:3, 2:"abc", 3:"three"}

class A(object):
    @rule
    def f(self): pass

    @rule
    def g(self): pass

    def h(self): pass

def test_get_rules():
    assert set(getRules(A)) == {('f', A.f), ('g', A.g)}

