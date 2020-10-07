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

    def copy(self):
        new_path = Path()
        new_path.type = self.type
        new_path.cost = self.cost
        new_path.nodes = self.nodes.copy()
        return new_path

    # Fixes runs to have the proper cost
    def fix(self, wild):
        if self.type is RUN:
            self.nodes.sort(reverse=False, key=lambda edg: edg.name[VAL_IDX])
        curr = self.nodes[0].name[VAL_IDX] - 1
        self.cost = 0
        for node in self.nodes:
            if node.name[VAL_IDX] == wild or node.name[SUIT_IDX] == 'J':
                self.cost -= 1
            else:
                self.cost += node.name[COST_VAL] - curr - 1
                curr = node.name[VAL_IDX]

    # Function used for ordering in the fix function
    def fix_func(self, node):
        return node.name[VAL_IDX]

    # Evaluates the number of points in an incomplete run. Out controls whether the game is out, as wild cards should
    # not be counted as points until the game is over
    def evaluate(self, wild, out=False, fits_hand=True):
        valid = True
        cost = 0
        if self.type is RUN:
            # fixes runs to have the correct cost
            self.fix(wild)
            if self.cost > 0:
                valid = False
        elif self.type is SET:
            if len(self.nodes) < 3:
                valid = False
        else:
            if len(self.nodes) < 3:
                valid = False
        # add up the points found in non-valid groupings
        valid = valid and fits_hand
        if not valid:
            for node in self.nodes:
                if node.name[VAL_IDX] == wild:
                    if out:
                        cost += 20
                    else:
                        cost += 0
                elif node.name[SUIT_IDX] == 'J':
                    if out:
                        cost += 50
                    else:
                        cost += 0
                else:
                    cost += node.name[VAL_IDX]
        return cost


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
    # An edge is a tuple consisting of a node and a cost

    def find_edges(self, hand, drawn=False):
        self.hand = hand
        # Turn all of the cards into nodes
        for card in hand:
            new_card = Node(name=card)
            self.nodes.append(new_card)

        # For each card, check what cards it can connect to
        for node in self.nodes:
            wild = False
            if (node.name[VAL_IDX] is len(hand) - 1 and drawn) or (node.name[VAL_IDX] is len(hand) and not drawn)\
                    or node.name[SUIT_IDX] == 'J':
                wild = True
            for check in self.nodes:
                # Check for self
                if check.name[VAL_IDX] is node.name[VAL_IDX] and check.name[SUIT_IDX] is node.name[SUIT_IDX] \
                        and node.name[DECK_IDX] is check.name[DECK_IDX]:
                    val = 1
                # Check for wildcard
                # If we are looking for edges on a hand that has just drawn, they have an extra card so wildcard is 1
                # less than the length of their hand.
                elif drawn and check.name[VAL_IDX] is len(hand)-1:
                    node.edges.append((check, WILD_VAL))
                elif check.name[VAL_IDX] is len(hand):
                    node.edges.append((check, WILD_VAL))
                elif check.name[SUIT_IDX] is "J":
                    node.edges.append((check, WILD_VAL))
                # Check for the same number
                # Wild check so that wild cards only have edges to other wild cards
                elif node.name[VAL_IDX] is check.name[VAL_IDX] and not wild:
                    node.edges.append((check, SET_VAL))
                # Check for the same suit
                elif node.name[SUIT_IDX] is check.name[SUIT_IDX] and not wild:
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
    # This method is heavily flawed and needs to be looked into. Currently use all_combo and evaluation functions to
    # determine when a hand has 0 points
    def complete_hand(self, hand):
        self.find_edges(hand)
        unused_nodes = []
        reserved_nodes = []
        for node in self.nodes:
            unused_nodes.append(node)
        while len(unused_nodes) > 0:
            # check if all of the unused nodes are wild cards. If they are, we can go out.
            if len(unused_nodes[0].edges) is 0:
                return False
            else:
                # Generates the longest path possible with the available nodes
                new_sub_graph = self.sub_graph(unused_nodes[0], unused_nodes)
                # Checks if the subgraph was valid, and if it was removes the cards used from the available pile
                if len(new_sub_graph.nodes) >= 3:
                    for sg_node in new_sub_graph.nodes:
                        if reserved_nodes.__contains__(sg_node):
                            return False
                        if unused_nodes.__contains__(sg_node):
                            unused_nodes.remove(sg_node)
                # If the path was NOT valid, check conditions to see if a valid path could be made
                else:
                    # If even using all the nodes a valid length path could not be made, return false
                    if len(unused_nodes) is len(self.nodes):
                        return False
                    longest_sub_graph = self.sub_graph(unused_nodes[0], self.nodes)
                    if len(longest_sub_graph.nodes) < 3:
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
    def sub_graph(self, node, free_nodes, path=None, allow_any=False):
        if path is None:
            path = Path()
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
            if curr_edge[COST_VAL] + path.cost < len(wildcards) or allow_any:
                if path.type is NO_TYPE:
                    if curr_edge[COST_VAL] < -1:
                        path.type = SET
                    elif curr_edge[COST_VAL] >= 0:
                        path.type = RUN
                elif path.type is SET:
                    if not curr_edge[COST_VAL] < -1:
                        break
                elif path.type is RUN:
                    if not curr_edge[COST_VAL] > 0:
                        break
                path.cost += curr_edge[COST_VAL]
                new_path = self.sub_graph(curr_edge[NODE], free_nodes, path, allow_any=allow_any)
                if len(new_path.nodes) > len(path.nodes):
                    path = new_path
        if len(path.nodes) < 3:
            if len(path.nodes) + len(wildcards) >= 3:
                path.add_node(wildcards.pop())
        return path

    # Check whether the input card (a node) is wild
    @staticmethod
    def wild_check(card, length, draw=False):
        if card.name[VAL_IDX] == length and not draw:
            return True
        elif card.name[VAL_IDX] == length - 1 and draw:
            return True
        elif card.name[SUIT_IDX] == 'J':
            return True
        else:
            return False

    # Creates every possible combination of cards possible for a hand
    def all_combo(self, hand, draw=False):
        self.find_edges(hand, drawn=draw)
        unused_nodes = []
        # Semi-sorts the nodes so that all cards are looked at before the wild cards.
        for node in self.nodes:
            if self.wild_check(node, len(self.nodes), draw):
                unused_nodes.append(node)
            else:
                unused_nodes.insert(0, node)
        curr_hand = []
        combinations = []
        return self.all_combinations(self.nodes[0], unused_nodes, unused_nodes, curr_hand, combinations, draw=draw)

    # This method returns a list of hands that have been organized into all possible arrangements
    # For every node, explore every valid neighbor. Move through using only unused nodes.
    # Argument explanation: node is the current card node, which is a list containing a value and a cost
    # nodes is the list of all nodes. This is used to regain the list of all nodes when a new hand arrangement is made
    # unused_nodes is the unused nodes for the current recursion
    # curr_hand is a list of the paths that can be made in the current recursion
    # combinations is a list of all the possible hands
    # path is the current path being built. If no path is provided, it will create a new path
    # draw indicates whether the hand currently holds an extra card
    def all_combinations(self, node, nodes, unused_nodes, curr_hand, combinations, path=None, draw=False):
        if path is None:
            path = Path()
        # add the new node to the path. I don't think the cost in the path is necessary
        path.add_node((node, 0))
        unused_nodes.remove(node)
        # When we run out of unused nodes, add the hand to the combinations and end
        if len(unused_nodes) is 0:
            curr_hand.append(path)
            combinations.append(curr_hand)
        else:
            neighbors = node.edges
            # Verify that the neighbors are valid to be added to the current path
            new_neighbors = []
            for neighbor in neighbors:
                # Check that nodes are unused and are correct for the type of path
                if unused_nodes.__contains__(neighbor[NODE]):
                    # Sets can have other set neighbors or wild cards added
                    if path.type is SET:
                        if neighbor[COST_VAL] <= -1:
                            new_neighbors.append(neighbor)
                    # Runs can have other run neighbors or wild cards added
                    elif path.type is RUN:
                        if neighbor[COST_VAL] >= -1:
                            new_neighbors.append(neighbor)
                    # If the path doesn't have a set yet, any neighbor can be added
                    else:
                        new_neighbors.append(neighbor)
            # If there are no valid neighbors, add the path to hand and start a new path in the hand
            if len(new_neighbors) == 0:
                curr_hand.append(path)
                self.all_combinations(unused_nodes[0], nodes, unused_nodes, curr_hand, combinations, draw=draw)
            # Create a new path with assumption nothing added to original card
            if len(unused_nodes) > 0:
                new_hand = curr_hand.copy()
                new_hand.append(path.copy())
                self.all_combinations(unused_nodes[0], nodes, unused_nodes.copy(), new_hand, combinations,
                                      draw=draw)
            # For each valid neighbor, add it to the path and explore what the hand looks like
            for neighbor in new_neighbors:
                # Add a type to the path if applicable
                # Need to avoid c5 W W d8 r8 being valid
                if path.type is NO_TYPE:
                    if neighbor[COST_VAL] < -1:
                        path.type = SET
                    elif neighbor[COST_VAL] >= 0:
                        path.type = RUN
                # Repeat for the new node
                self.all_combinations(neighbor[NODE], nodes, unused_nodes.copy(),
                                      curr_hand.copy(), combinations, path.copy(), draw)

        return combinations

    # Returns a score for a hand grouping.
    # A hand if a list of paths
    @staticmethod
    def evaluate_hand(hand, drawn=False, out=False):
        wild = 0
        cost = 0
        # Determines the wild card value
        for path in hand:
            wild += len(path.nodes)
        if drawn:
            wild -= 1
        for path in hand:
            cost += path.evaluate(wild, out)
        return cost

    # Evaluates every combination of hands returned by all_combo and returns the lowest score possible for the current
    # hand
    @staticmethod
    def evaluate_hands(combos, drawn=False, out=False):
        lowest = 1000
        for comb in combos:
            value = HandGraph.evaluate_hand(comb, drawn=drawn, out=out)
            if value < lowest:
                lowest = value
        return lowest

    # Checks for wild cards but using the tuple format used by the deck
    @staticmethod
    def wild_check_tuple(card, length, draw=False):
        if card[VAL_IDX] == length and not draw:
            return True
        elif card[VAL_IDX] == length - 1 and draw:
            return True
        elif card[SUIT_IDX] == 'J':
            return True
        else:
            return False

# Main method for testing different functions
if __name__ == "__main__":
    test_hand = [('c', 11, 1), ('J', 0, 2), ('c', 5, 1), ('c', 10, 0)]

    # [('r', 6, 0), ('r', 5, 1), ('r', 7, 1), ('c', 11, 0), ('r', 11, 1), ('d', 8, 0), ('r', 8, 0), ('r', 10, 0), ('d', 9, 0), ('J', 0, 1), ('r', 10, 1)]
    graph = HandGraph()
    """
    
    path = Path()
    path.add_node((('J', 0, 1), -1))
    path.add_node((('J', 0, 2), -1))
    path.add_node((('r', 5, 1), -1))
    print(path.evaluate(3, out=True))

    """
    all_combos = graph.all_combo(test_hand, False)
    low = 1000
    high = 0
    i = 0
    for combo in all_combos:
        i += 1
        for group in combo:
            print(group, end=' ')
        print()
        val = graph.evaluate_hand(combo)
        if val < low:
            low = val
        if val > high:
            high = val
    print("Number of combinations: ", len(all_combos))
    print("Highest scoring hand: ", high)
    print("Lowest scoring hand: ", low)
        


    """
    [('c', 7, 0), ('s', 4, 0), ('c', 6, 1), ('c', 6, 0)]
10's round
[('r', 5, 0), ('r', 6, 1), ('r', 7, 1), ('c', 11, 0), ('r', 11, 1), ('d', 8, 0), ('r', 8, 0), ('r', 10, 0), ('d', 9, 0), ('c', 10, 1)]
11's round
[('h', 3, 1), ('s', 4, 1), ('c', 10, 0), ('r', 4, 1), ('c', 9, 1), ('h', 11, 1), ('r', 3, 0), ('h', 4, 1), ('r', 11, 0), ('r', 4, 0), ('c', 12, 0)]
12's round
[('s', 6, 1), ('s', 7, 1), ('c', 6, 0), ('d', 8, 1), ('h', 8, 0), ('s', 7, 0), ('c', 7, 1), ('r', 12, 0), ('d', 6, 0), ('s', 7, 0), ('s', 7, 1), ('d', 6, 1)]"""

