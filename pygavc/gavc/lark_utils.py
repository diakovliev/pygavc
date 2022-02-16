import lark

class TreeHelper:
    def __init__(self, tree):
        self.__tree = tree

    def tree(self):
        return self.__tree

    def children(self):
        return ( TreeHelper(c) for c in self.__tree.children )

    def __len__(self):
        return len(self.__tree.children)

    def __subtree_by_name(self, name):
        for element in self.__tree.children:
            if name == element.data: return TreeHelper(element)
        return None

    def tree_by_path(self, path):
        pelems = path.split("/")
        current_tree = self
        for pelem in pelems:
            current_tree = current_tree.__subtree_by_name(pelem)
            if not current_tree:
                return None
        return current_tree

    def first_value(self, default_value = None):
        if len(self) == 0:
            return default_value
        if not isinstance(self.__tree.children[0], lark.Tree):
            return self.__tree.children[0]
        return default_value
