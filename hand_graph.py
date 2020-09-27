class Path:
    def __init__(self):
        self.type = -1
        self.cost = 0
        self.nodes = []

    def add_node(self, edge):
        self.cost += edge[1]
        self.nodes.append(edge[0])

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
DECK_IDX = 2
SET_VAL = -2
WILD_VAL = -1
SET = 0
RUN = 1
NODE = 0
NO_TYPE = -1


class HandGraph:
    def __init__(self):
        self.nodes = []
        self.hand = []

    # the cost to move between two nodes in a run is the absolute difference between them -1
    # the cost to use a wildcard is -1
    # the cost to move between two nodes in a set is -2.
    # A loop with non-negative cost cannot bring in negative edges and a loop with negative cost
    # cannot bring in non-negative edges.
    # Look for every path that goes through at least three nodes and has either a cost of 0
    # or a cost of < -2

    def find_edges(self, hand, drawn=False):
        self.hand = hand
        # Turn all of the cards into nodes
        for card in hand:
            new_card = Node(name=card)
            self.nodes.append(new_card)

        # For each card, check what cards it can connect to
        for node in self.nodes:
            for check in self.nodes:
                # Check for self
                if check.name[VAL_IDX] is node.name[VAL_IDX] and check.name[SUIT_IDX] is node.name[SUIT_IDX] \
                        and node.name[DECK_IDX] is node.name[DECK_IDX]:
                    val = 1
                # Check for wildcard
                # If we are looking for edges on a hand that has just drawn, they have an extra card so wildcard is 1
                # less than the length of their hand.
                if drawn:
                    if check.name[VAL_IDX] is len(hand)-1:
                        node.edges.append((check, WILD_VAL))
                elif check.name[VAL_IDX] is len(hand):
                    node.edges.append((check, WILD_VAL))
                # Check for the same number
                elif node.name[VAL_IDX] is check.name[VAL_IDX]:
                    node.edges.append((check, SET_VAL))
                # Check for the same suit
                elif node.name[SUIT_IDX] is check.name[SUIT_IDX]:
                    node.edges.append((check, abs(node.name[VAL_IDX] - check.name[VAL_IDX])-1))

    # To check for a complete hand, try to make it so that every node in the graph belongs to a valid subgraph of size
    # at least 3. To do this, start by checking that each node is at least connected to something. Will need a fix for
    # the current wild card system.
    # Option 2: Build the longest path for the first card. Using the remaining cards, try to build the longest path for
    # the next card that is not currently in a valid path. If no such path exists, go back to a previous path and look
    # for an alternative. Repeat until there are either no alternatives or a success is found.
    # This might be a constraints problem
    # If you fail with the unused nodes, try with all the nodes. If still no path exists, fail. If a path exists,
    # reserve those nodes as used and go back and try to build a new path for earlier cards not using the now reserved
    # cards. At some point, need to have an exit condition for repeated failure.
    def complete_hand(self, hand):
        self.find_edges(hand)
        unused_nodes = []
        reserved_nodes = []
        for node in self.nodes:
            unused_nodes.append(node)
        while len(unused_nodes) > 0:
            if len(unused_nodes[0].edges) is 0:
                return False
            else:
                # Generates the longest path possible with the available nodes
                new_sub_graph = self.sub_graph(unused_nodes[0], unused_nodes)
                # Checks if the subgraph was valid, and if it was removes the cards used from the available pile
                if len(new_sub_graph.nodes) >= 3:
                    for sg_node in new_sub_graph.nodes:
                        if unused_nodes.__contains__(sg_node):
                            unused_nodes.remove(sg_node)
                # If the path was NOT valid, check conditions to see if a valid path could be made
                else:
                    # If even using all the nodes a valid length path could not be made, return false
                    if len(unused_nodes) is len(self.nodes):
                        return False
                    longest_sub_graph = self.sub_graph(unused_nodes[0], self.nodes)
                    if len(longest_sub_graph) < 3:
                        return False
                    # If a valid path COULD be made, reserve those nodes and try again.
                    else:
                        for card in longest_sub_graph.nodes:
                            if reserved_nodes.__contains__(card):
                                return False
                            else:
                                reserved_nodes.append(card)
                        unused_nodes = self.nodes
        # If every node was able to be used, the hand can go out.
        return True

    # Generates the largest valid subgraph that it can for the node using the remaining nodes.
    # Node indicates the card to start the path from. Free_nodes indicates the nodes available to use in the set.
    # path indicates the currently progressing path. Allow_any indicates whether the path cost needs to be valid or not
    def sub_graph(self, node, free_nodes, path=Path(), allow_any=False):
        path.nodes.append(node)
        neighbors = node.edges
        possibles = []
        wildcards = []
        for edge in neighbors:
            # Check if we have not yet used the neighbor
            if free_nodes.__contains__(edge[NODE]):
                # Check if the node is a wildcard. If it is, add it to wildcards
                if edge[NODE].name[SUIT_IDX] is 'J' or edge[NODE].name[VAL_IDX] is len(self.hand):
                    wildcards.append(edge)
                # If the card is not wild, check if it is adjacent to the current node
                # Makes sure the card isn't already in the path, needs a fix because five crowns decks are doubled
                elif not path.nodes.__contains__(edge[NODE]):
                    # If the path does not yet have a type, add all adjacent as possibles
                    if path.type is NO_TYPE:
                        possibles.append(edge)
                    # If the type is set, only add edges with the correct edge cost
                    elif path.type is SET:
                        if edge[COST_VAL] < 0:
                            possibles.append(edge)
                    # If the type is run, only add edges with the correct edge cost
                    elif path.type is RUN:
                        if edge[COST_VAL] >= 0:
                            possibles.append(edge)
        possibles.sort(reverse=True, key=lambda edg: edg[COST_VAL])
        # While there are neighbors, go to that and try to keep going
        while len(possibles) > 0:
            curr_edge = possibles.pop()
            if curr_edge[COST_VAL] < len(wildcards) or allow_any:
                if path.type is NO_TYPE:
                    if curr_edge[COST_VAL] < -1:
                        path.type = SET
                    elif curr_edge[COST_VAL] >= 0:
                        path.type = RUN
                path.cost += curr_edge[COST_VAL]
                new_path = self.sub_graph(curr_edge[NODE], free_nodes, path, allow_any)
                if len(new_path.nodes) > len(path.nodes):
                    path = new_path
        if len(path.nodes) < 3:
            if len(path.nodes) + len(wildcards) >= 3:
                path.add_node(wildcards.pop())
        return path


if __name__ == "__main__":
    test_hand = [("c", 13, 0), ("r", 13, 0), ("h", 10, 0), ("J", 0, 0), ("h", 10, 1), ("c", 12, 0), ("h", 12, 0),
                 ("d", 12, 0), ("r", 12, 0), ("c", 7, 0)]
    graph = HandGraph()

    print(graph.complete_hand(test_hand))

    """
    for group in graph.all_groups(test_hand):
        print(group)"""

