from collections import deque
class Node:
    def __init__(self, xpath):
        self.xpath = xpath
        self.children = []

    def add_child(self, child):
        self.children.append(child)

def build_dom_tree(xpaths):
    nodes = {}
    for xpath in xpaths:
        parts = xpath.split('/')[1:]
        node_key = '/'.join(parts)
        if node_key not in nodes:
            nodes[node_key] = Node(xpath)
        parent_key = '/'.join(parts[:-1])
        if parent_key:
            if parent_key not in nodes:
                nodes[parent_key] = Node('/'.join(xpath.split('/')[:-1]))
            nodes[parent_key].add_child(nodes[node_key])
    for node_key, node in nodes.items():
        if not any(node.xpath == parent for parent in nodes if node.xpath != nodes[parent].xpath):
            return node

def find_leaf_nodes(node):
    leaf_nodes = []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        if not current.children:
            leaf_nodes.append(current.xpath)
        else:
            queue.extend(current.children)
    return leaf_nodes