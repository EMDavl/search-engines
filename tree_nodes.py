from pygtrie import StringTrie


class TreeNode:
    left = None
    right = None

    def eval(self, index_tree: StringTrie) -> set[int]:
        pass


class NotNode(TreeNode):
    val: TreeNode
    cached_entries = set()

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"NOT - [{self.val}]"

    def eval(self, index_tree: StringTrie) -> set[int]:
        child_set = self.val.eval(index_tree)
        if not NotNode.cached_entries:
            for val in index_tree.values():
                for val2 in val:
                    NotNode.cached_entries.add(val2)
        all_entries = NotNode.cached_entries
        return all_entries.difference(child_set)


class AndNode(TreeNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"AND - [{self.left} {self.right}]"

    def eval(self, index_tree: StringTrie) -> set[int]:
        left_res = self.left.eval(index_tree)
        right_res = self.right.eval(index_tree)
        return left_res.intersection(right_res)


class OrNode(TreeNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"OR - [{self.left} {self.right}]"

    def eval(self, index_tree: StringTrie) -> set[int]:
        left_res = self.left.eval(index_tree)
        right_res = self.right.eval(index_tree)
        return left_res.union(right_res)


class LexemeNode(TreeNode):
    val: str

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"LEX - {self.val}"

    def eval(self, index_tree: StringTrie) -> set[int]:
        return set(index_tree.get(self.val))
