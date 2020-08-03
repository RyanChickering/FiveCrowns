class Path:
    def __init__(self):
        self.type = -1
        self.cost = 0
        self.nodes = []

    def __str__(self):
        output = ''
        for node in self.nodes:
            output += str(node.__str__())
        output += " cost: " + str(self.cost)
        if self.type is SET:
            output += " type: set"
        elif self.type is RUN:
            output += " type: run"
        else:
            output += " type: no type"
        return output


class Node:
    def __init__(self, name=""):
        self.name = name
        self.edges = []

    def __str__(self):
        return self.name


VAL_IDX = 1
SUIT_IDX = 0
COST_VAL = 1
SET_VAL = -2
WILD_VAL = -1
SET = 0
RUN = 1
NODE = 0
NO_TYPE = -1


class HandGraph:
    def __init__(self):
        self.nodes = []

    # the cost to move between two nodes in a run is the absolute difference between them -1
    # the cost to use a wildcard is -1
    # the cost to move between two nodes in a set is -2.
    # A loop with non-negative cost cannot bring in negative edges and a loop with negative cost
    # cannot bring in non-negative edges.
    # Look for every path that goes through at least three nodes and has either a cost of 0
    # or a cost of < -2

    def find_edges(self, hand):

        # Turn all of the cards into nodes
        for card in hand:
            new_card = Node(name=card)
            self.nodes.append(new_card)

        # For each card, check what cards it can connect to
        for node in self.nodes:
            for check in self.nodes:
                # Check for self
                if check.name[VAL_IDX] is node.name[VAL_IDX] and check.name[SUIT_IDX] is node.name[SUIT_IDX]:
                    val = 1
                # Check for wildcard
                elif check.name[VAL_IDX] is len(hand):
                    node.edges.append((check, WILD_VAL))
                # Check for the same number
                elif node.name[VAL_IDX] is check.name[VAL_IDX]:
                    node.edges.append((check, SET_VAL))
                # Check for the same suit
                elif node.name[SUIT_IDX] is check.name[SUIT_IDX]:
                    node.edges.append((check, abs(node.name[VAL_IDX] - check.name[VAL_IDX])-1))

    # Have a list of nodes which each contain a list of edges. Edges consist of a tuple of another node and a cost
    # to move to that node. In order to find paths that are at least 3 long and have the correct cost, need to
    # recursively build a path by going through the node links... or something.
    def find_groups(self, curr_node, path=Path()):
        path.nodes.append(curr_node)
        unvisited = curr_node.edges
        possibles = []
        for edge in unvisited:
            if not path.nodes.__contains__(edge[NODE]):
                if path.type is NO_TYPE:
                    possibles.append(edge)
                elif path.type is SET:
                    if edge[COST_VAL] < 0:
                        possibles.append(edge)
                elif path.type is RUN:
                    if edge[COST_VAL] >= 0:
                        possibles.append(edge)
        possibles.sort(reverse=True, key=lambda edg: edg[COST_VAL])
        while len(possibles) > 0:
            curr_edge = possibles.pop()
            if path.type is NO_TYPE:
                if curr_edge[COST_VAL] < -1:
                    path.type = SET
                elif curr_edge[COST_VAL] >= 0:
                    path.type = RUN
            path.cost += curr_edge[COST_VAL]
            return self.find_groups(curr_edge[NODE], path)
        return path

    def all_groups(self, hand):
        self.find_edges(hand)
        groups = []
        for node in self.nodes:
            groups.append(self.find_groups(node, path=Path()))
        return groups


if __name__ == "__main__":
    test_hand = [('star', 10), ('spade', 7), ('diamond', 10), ('club', 11), ('heart', 6),
                     ('heart', 3), ('star', 9), ('heart', 10)]
    graph = HandGraph()
    for group in graph.all_groups(test_hand):
        print(group)

