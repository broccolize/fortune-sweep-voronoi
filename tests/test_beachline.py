import math
import random
import pytest
from fortune.beachline import Arc, BeachLine
from fortune.geometry import Point


@pytest.mark.parametrize('seed', range(5))
def test_avl_random_insert_and_delete(seed):
    rng, tree, expected = random.Random(seed), BeachLine(), []
    for i in range(600):
        index = rng.randrange(len(expected) + 1)
        new = Arc(i)
        tree.insert_after(expected[index - 1] if index else None, new)
        expected.insert(index, new)
        tree.validate()
        assert list(tree) == expected
    assert tree.root.height < 1.45 * math.log2(len(expected) + 2) + 1
    rng.shuffle(expected)
    for node in expected:
        tree.remove(node)
        tree.validate()
    assert tree.root is None and tree.count == 0


def test_ordered_locate_for_equal_height_sites():
    tree = BeachLine()
    points = [Point(-2, 1), Point(0, 1), Point(2, 1)]
    previous = None
    for i in range(3):
        new = Arc(i)
        tree.insert_after(previous, new)
        previous = new
    assert tree.locate(-10, 0, points).site == 0
    assert tree.locate(0, 0, points).site == 1
    assert tree.locate(10, 0, points).site == 2


def test_removed_arc_cannot_be_deleted_again():
    tree, node = BeachLine(), Arc(0)
    tree.insert_after(None, node)
    tree.remove(node)
    with pytest.raises(ValueError):
        tree.remove(node)
