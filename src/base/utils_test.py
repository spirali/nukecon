from utils import make_partitions, combinations

def test_combinations():
    s = [ "A", "B", "C", "D" ]
    assert [["A"], ["B"], ["C"], ["D"]] == combinations(s, 1)
    assert [['A', 'B'],
            ['A', 'C'],
            ['A', 'D'],
            ['B', 'C'],
            ['B', 'D'],
            ['C', 'D']] == combinations(s, 2)
    assert [['A', 'B', 'C'],
            ['A', 'B', 'D'],
            ['A', 'C', 'D'],
            ['B', 'C', 'D']] == combinations(s, 3)
    assert [['A', 'B', 'C', 'D']] == combinations(s, 4)

def test_make_parittions():
    def f(*x):
        return frozenset(x)
    def make_set(m):
        return frozenset(map(frozenset, m))
    s = (1, 2, 3, 4)
    print make_partitions(s, 4)
    assert frozenset([f((1, 2, 3, 4),)]) == make_set(make_partitions(s, 1))
    assert frozenset([
        f((1,), (2, 3, 4)),
        f((2,), (3, 4, 1)),
        f((3,), (4, 1, 2)),
        f((4,), (1, 2, 3)),
        f((1, 2), (3, 4)),
        f((2, 3), (4, 1)),
        ]) == make_set(make_partitions(s, 2))

    assert frozenset([
        f((1,), (2,), (3, 4)),
        f((2,), (3,), (4, 1)),
        f((3,), (4,), (1, 2)),
        f((4,), (1,), (2, 3)),
        ]) == make_set(make_partitions(s, 3))

    assert frozenset([
        f((1,), (2,), (3,), (4,)),
        ]) == make_set(make_partitions(s, 4))
