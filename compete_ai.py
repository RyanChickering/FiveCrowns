import player
import hand_graph

"""
AI whose goal is to create sets and go out.

"""

BASE = 7


class Player(player.Player):

    # Method that decides what to draw. If the discard matches a needed card, pick it up. Otherwise, draw from the
    # deck.
    def draw(self, game):
        needed = []
        self.identify_sets(needed, game)
        temp = game.discard_pile.pop()
        if hand_graph.HandGraph.wild_check_tuple(temp, game.round_num, draw=False):
            self.hand.append(temp)
            return
        for card in needed:
            if temp[hand_graph.SUIT_IDX] == card[hand_graph.SUIT_IDX] or card[hand_graph.SUIT_IDX] is 'n':
                if temp[hand_graph.VAL_IDX] == card[hand_graph.VAL_IDX]:
                    self.hand.append(temp)
                    return
        game.discard_pile.append(temp)
        temp = game.deck.draw()
        self.hand.append(temp)

    # Identify the most useless card currently in the hand and throw it away
    def discard(self, game):
        graph = hand_graph.HandGraph()
        graph.find_edges(self.hand, drawn=True)
        useless = []
        # First, look for cards that aren't related to other cards
        for node in graph.nodes:
            # If a card has no edges and is not wild, it is useless
            if len(node.edges) is 0 and not hand_graph.HandGraph.wild_check(node, game.round_num):
                useless.append(node)
            # Cards that are distantly related through a run are not useful if the run length is longer than
            # the hand
            for edge in node.edges:
                if edge[hand_graph.COST_VAL] < game.round_num:
                    break
        # Sort the useless cards and discard the highest
        if len(useless) > 0 and useless is not None:
            useless.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            return self.node_in_hand(useless.pop())
        else:
            # If useless cards were not found, get the best hand combination currently available
            needed = []
            best = self.identify_sets(needed, game)
            solo_path = hand_graph.Node(('n', 0, 0))
            worst = 0
            worst_path = hand_graph.Path()
            # Go through the paths in best and look for the one that currently costs the most points and get rid of
            # cards from that.
            for path in best:
                if len(path.nodes) == 1:
                    if path.nodes[0].name[hand_graph.COST_VAL] > solo_path.name[hand_graph.COST_VAL]:
                        solo_path = path.nodes[0]
                if self.path_eval(path, game.round_num) is not 0:
                    value = path.evaluate(game.round_num)
                    if value > worst:
                        worst = value
                        worst_path = path
            worst_path.nodes.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            if len(worst_path.nodes) > 0:
                if worst_path.nodes[0].name[hand_graph.VAL_IDX] > solo_path.name[hand_graph.COST_VAL]:
                    return self.node_in_hand(worst_path.nodes.pop())
            if solo_path.name[hand_graph.COST_VAL] > 0:
                return self.node_in_hand(solo_path)
            # If there were no non-0 cost paths and no paths of length 1, look for a path of length four that can
            # give up a node. If you can't find that, throw out a card protecting the lowest value cards
            for path in best:
                if len(path.nodes) == 4:
                    # Since all other sets go together and this is a set of 4, can pitch any card from the set and still
                    # go out
                    if path.type is hand_graph.SET:
                        return self.node_in_hand(path.nodes[0])
                    elif path.type is hand_graph.RUN:
                        i = 0
                        # Runs are ordered from smallest to largest, so iterate through until you find a non wild and
                        # pitch it
                        path.fix(game.round_num)
                        while i < len(path.nodes) and not graph.wild_check(path.nodes[i], game.round_num):
                            i += 1
                        if i < len(path.nodes):
                            return self.node_in_hand(path.nodes[i])
            # If there were no sets of 4, need to go through all the sets and find the one with the lowest cost (if the
            # cards counted) and then throw out the highest card in it
            lowest = 1000
            candidate = hand_graph.Path()
            for path in best:
                value = path.evaluate(game.round_num, fits_hand=False)
                if value < lowest:
                    lowest = value
                    candidate = path
            candidate.nodes.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            return self.node_in_hand(candidate.nodes.pop())

    def node_in_hand(self, node):
        for card in self.hand:
            if node.name == card:
                self.hand.remove(card)
                return card

    def identify_sets(self, needed, game):
        graph = hand_graph.HandGraph()
        combos = graph.all_combo(self.hand, False)
        # get all the possible hand combinations out, look for ones with high average path length
        # want to keep hand combinations with the fewest cards needed to go out on hand.
        best = []
        lowest = 1000
        for combo in combos:
            value = self.evaluate(combo)
            if value < lowest:
                lowest = value
                best = combo
        for path in best:
            if self.path_eval(path, game.round_num) != 0 and len(path.nodes) > 1:
                self.path_tracer(path, needed, game)
        return best

    # adds needed cards to the needed list
    def path_tracer(self, path, needed, game):
        if path.type is hand_graph.RUN:
            path.fix(game.round_num)
            suit = 'n'
            run = []
            # need to trace through the run and find which cards are missing
            for node in path.nodes:
                if not hand_graph.HandGraph.wild_check(node, game.round_num, False):
                    suit = node.name[hand_graph.SUIT_IDX]
                    run.append(node.name[hand_graph.VAL_IDX])
            curr = run[0]
            for item in run:
                for i in range(item-curr-1):
                    needed.append((suit, curr+i, 0))
                curr = item
        elif path.type is hand_graph.SET:
            # look for any non wild members of the set and that is the card that you need
            for node in path.nodes:
                if not hand_graph.HandGraph.wild_check(node, game.round_num, False):
                    needed.append(('n', node.name[hand_graph.VAL_IDX], 0))
        elif path.type is hand_graph.NO_TYPE:
            # Look for any non-wild cards and then add all cards adjacent to that one
            for node in path.nodes:
                if not hand_graph.HandGraph.wild_check(node, game.round_num, False):
                    needed.append(('n', node.name[hand_graph.VAL_IDX], 0))
                    if node.name[hand_graph.VAL_IDX] < 13:
                        needed.append((node.name[hand_graph.SUIT_IDX], node.name[hand_graph.VAL_IDX] + 1, 0))
                    if node.name[hand_graph.VAL_IDX] > 3:
                        needed.append((node.name[hand_graph.SUIT_IDX], node.name[hand_graph.VAL_IDX] + 1, 0))
            # if there were no wild cards, you just have a loose stack of wilds which seems unlikely


    # Returns how many cards are needed for a particular hand to go out
    def evaluate(self, hand):
        wild = 0
        for path in hand:
            wild += len(path.nodes)
        needed = 0
        for path in hand:
            needed += self.path_eval(path, wild)
        return needed

    def path_eval(self, path, wild):
        needed  = 0
        path.fix(wild)
        value = path.evaluate(wild)
        if path.cost > 0:
            needed += value
        if value == 0:
            needed += value
        else:
            i = BASE
            t_path = path.copy()
            while t_path.evaluate(wild) != 0:
                joker = hand_graph.Node(('J', 0, i))
                t_path.add_node((joker, -1))
                i += 1
            needed += i - BASE
        return needed
