import player
import hand_graph

POINT_VAL = 1


class Player(player.Player):
    def draw(self, game):
        self.hand.append(game.discard)

    def discard(self, game):
        groups = self.build_groups()
        worst_set = groups[0]
        # Checks if there is a card that is not connected to anything else.
        choice = self.most_useless_card()
        # If there is no useless card by itself, have to make a choice about what to discard
        if choice is not None:
            game.discard = self.hand.index(choice)
            return
        for item in groups:
            if item[POINT_VAL] > worst_set[POINT_VAL]:
                worst_set = item
        # Once the worst set is determined, sort it by point value and then throw out the highest one.
        choice = 0
        game.discard = self.hand.pop(choice)

    def most_useless_card(self):
        graph = hand_graph.HandGraph()
        graph.find_edges(self.hand)
        useless = []
        for node in graph.nodes:
            if len(node.edges) is 0:
                useless.append(node)
        if len(useless) > 0:
            return sorted(useless, key=lambda crd: crd[1]).pop()
        else:
            return None

    # Objective: build the hand into the set of groups that reduce the score the most
    # Similar system to trying to go out. Attempt to build the longest set for each card. Prioritize sets that save
    # More points. When building these groups, will have an extra card in the hand so you have to account for that.
    # 2 groups of 3 in the 5s round is not useful.
    # Build a group, and then store the group and the points that it is saving or not into a tuple.
    # This method will be useful both for determining cards to discard and cards to draw. Will probably run for each of
    # those actions. What is the difference between when you have too many cards or not?
    def build_groups(self, drawn=True):
        graph = hand_graph.HandGraph()
        graph.find_edges(self.hand, drawn)
        # Keep track of nodes used in finished sets as well as nodes used in unfinished sets.
        groups = []
        unused_nodes = []
        reserved_nodes = []
        useless = []
        for node in graph.nodes:
            unused_nodes.append(node)
        while len(unused_nodes) > 0:
            if len(unused_nodes[0].edges) is 0:
                groups.append((unused_nodes.pop(0), unused_nodes[0].name[POINT_VAL]))
            else:
                # Generates the longest path possible with the available nodes
                new_sub_graph = graph.sub_graph(unused_nodes[0], unused_nodes, allow_any=True)
                # Checks if the subgraph was valid, and if it was removes the cards used from the available pile
                if len(new_sub_graph.nodes) >= 3:
                    for sg_node in new_sub_graph.nodes:
                        if unused_nodes.__contains__(sg_node):
                            unused_nodes.remove(sg_node)
                # Have to determine the best way to use the cards that we have. First look if they can be used in a
                # complete set.
                # If the path was NOT valid, check conditions to see if a valid path could be made
                else:
                    # If even using all the nodes a valid length path could not be made, return false
                    if len(unused_nodes) is len(graph.nodes):
                        return False
                    longest_sub_graph = graph.sub_graph(unused_nodes[0], graph.nodes)
                    if len(longest_sub_graph) < 3:
                        return False
                    # If a valid path COULD be made, reserve those nodes and try again.
                    else:
                        for card in longest_sub_graph.nodes:
                            if reserved_nodes.__contains__(card):
                                unused_nodes.pop(0)
                            else:
                                reserved_nodes.append(card)
                        unused_nodes = graph.nodes
        # Return the set of groups and the set of useless cards.
        return groups + useless

    # Determine the card that will reduce the score of the hand the most
    def determine_need(self):
        return 2
