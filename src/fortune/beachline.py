"""An AVL sequence of arcs, with O(1) links to neighbouring arcs.

Nodes have stable identities: deletion transplants the actual successor node
rather than copying a payload, because queued events refer to arc objects.
"""

from dataclasses import dataclass

from .geometry import breakpoint_x


@dataclass(eq=False, slots=True)
class Arc:
    site: int
    left: "Arc | None" = None
    right: "Arc | None" = None
    parent: "Arc | None" = None
    prev: "Arc | None" = None
    next: "Arc | None" = None
    height: int = 1
    generation: int = 0
    alive: bool = True


def height(node):
    return node.height if node else 0


def update(node):
    node.height = 1 + max(height(node.left), height(node.right))


class BeachLine:
    def __init__(self):
        self.root = None
        self.first = None
        self.count = 0
        self.max_height = 0

    def _replace(self, old, new):
        parent = old.parent
        if parent is None:
            self.root = new
        elif parent.left is old:
            parent.left = new
        else:
            parent.right = new
        if new:
            new.parent = parent

    def _left(self, node):
        pivot = node.right
        self._replace(node, pivot)
        node.right = pivot.left
        if node.right:
            node.right.parent = node
        pivot.left, node.parent = node, pivot
        update(node)
        update(pivot)
        return pivot

    def _right(self, node):
        pivot = node.left
        self._replace(node, pivot)
        node.left = pivot.right
        if node.left:
            node.left.parent = node
        pivot.right, node.parent = node, pivot
        update(node)
        update(pivot)
        return pivot

    def _rebalance(self, node):
        while node:
            update(node)
            balance = height(node.left) - height(node.right)
            if balance > 1:
                if height(node.left.left) < height(node.left.right):
                    self._left(node.left)
                node = self._right(node)
            elif balance < -1:
                if height(node.right.right) < height(node.right.left):
                    self._right(node.right)
                node = self._left(node)
            node = node.parent
        self.max_height = max(self.max_height, height(self.root))

    def insert_after(self, before, new):
        if not new.alive or new.parent or new.left or new.right:
            raise ValueError("Insert a fresh unattached arc")
        if before is None:
            if self.root:
                anchor = self.first
                anchor.left = new
                new.parent = anchor
                new.next, anchor.prev, self.first = anchor, new, new
            else:
                self.root = self.first = new
        else:
            if not before.alive:
                raise ValueError("Insertion anchor is not live")
            anchor = before
            if before.right:
                anchor = before.right
                while anchor.left:
                    anchor = anchor.left
                anchor.left = new
            else:
                anchor.right = new
            new.parent = anchor
            new.prev, new.next = before, before.next
            if before.next:
                before.next.prev = new
            before.next = new
        self.count += 1
        self._rebalance(new)

    def remove(self, node):
        if not node.alive:
            raise ValueError("Arc has already been removed")
        if node.prev:
            node.prev.next = node.next
        else:
            self.first = node.next
        if node.next:
            node.next.prev = node.prev
        if node.left and node.right:
            successor = node.right
            while successor.left:
                successor = successor.left
            if successor.parent is node:
                start = successor
            else:
                start = successor.parent
                self._replace(successor, successor.right)
                successor.right = node.right
                successor.right.parent = successor
            self._replace(node, successor)
            successor.left = node.left
            successor.left.parent = successor
            update(successor)
        else:
            start = node.parent
            self._replace(node, node.left or node.right)
        node.alive = False
        node.generation += 1
        node.left = node.right = node.parent = None
        self.count -= 1
        self._rebalance(start)

    def locate(self, x, directrix, points):
        node = self.root
        while node:
            if node.prev and x < breakpoint_x(
                points[node.prev.site], points[node.site], directrix
            ):
                node = node.left
            elif node.next and x > breakpoint_x(
                points[node.site], points[node.next.site], directrix
            ):
                node = node.right
            else:
                return node
        raise ArithmeticError("Beach-line search escaped its ordered arcs")

    def __iter__(self):
        node = self.first
        while node:
            yield node
            node = node.next

    def validate(self):
        """Expensive debug invariant check; deliberately not in production loops."""
        order = []

        def walk(node, parent):
            if node is None:
                return 0
            assert node.alive and node.parent is parent
            lh = walk(node.left, node)
            order.append(node)
            rh = walk(node.right, node)
            assert abs(lh - rh) <= 1
            assert node.height == 1 + max(lh, rh)
            return node.height

        walk(self.root, None)
        assert len(order) == self.count
        assert list(self) == order
        for i, arc in enumerate(order):
            assert arc.prev is (order[i - 1] if i else None)
            assert arc.next is (order[i + 1] if i + 1 < len(order) else None)
        return True
