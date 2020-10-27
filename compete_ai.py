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
            # If a card is wild, it is useful
            if not hand_graph.HandGraph.wild_check(node, game.round_num):
                if len(node.edges) is 0:
                    useless.append(node)
                    break
                # Cards that are distantly related through a run are not useful if the run length is longer than
                # the hand. Cards that only have distant runs or wild relations are not useful
                useful = False
                for edge in node.edges:
                    if edge[hand_graph.COST_VAL] < game.round_num and not \
                            hand_graph.HandGraph.wild_check(edge[0], game.round_num):
                        useful = True
                        break
                if not useful:
                    useless.append(node)
        # Sort the useless cards and discard the highest
        if len(useless) > 0 and useless is not None:
            useless.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            return self.node_in_hand(useless.pop())
        else:
            # If useless cards were not found, get the best hand combination currently available
            needed = []
            best = self.identify_sets(needed, game)
            # Checks for a path of only length 1
            solo_path = hand_graph.Node(('n', 0, 0))
            worst = 0
            worst_path = hand_graph.Path()
            # Go through the paths in best and look for the one that currently needs the most cards to go out
            # and throw from that
            for path in best:
                cards_needed = self.path_eval(path, game.round_num)
                if cards_needed > worst:
                    worst = cards_needed
                    worst_path = path
                if len(path.nodes) == 1:
                    if path.nodes[0].name[hand_graph.COST_VAL] > solo_path.name[hand_graph.COST_VAL]:
                        solo_path = path.nodes[0]
            worst_path.nodes.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX], reverse=True)
            if len(worst_path.nodes) > 0:
                i = 0
                while hand_graph.HandGraph.wild_check(worst_path.nodes[i], game.round_num):
                    i += 1
                return self.node_in_hand(worst_path.nodes.pop(i))
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
                value = path.evaluate(game.round_num, out=True, fits_hand=False)
                if value < lowest:
                    lowest = value
                    candidate = path
            candidate.nodes.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX], reverse=True)
            i = 0
            while i < len(candidate.nodes)-1 and not graph.wild_check(candidate.nodes[i], game.round_num, draw=True):
                i += 1
            return self.node_in_hand(candidate.nodes.pop(i))

    def node_in_hand(self, node):
        for card in self.hand:
            if node.name == card:
                self.hand.remove(card)
                return card

    def identify_sets(self, needed, game):
        graph = hand_graph.HandGraph()
        if len(self.hand) > game.round_num:
            combos = graph.all_combo(self.hand, True)
        else:
            combos = graph.all_combo(self.hand, False)
        # get all the possible hand combinations out, look for ones with high average path length
        # want to keep hand combinations with the fewest cards needed to go out on hand.
        best = []
        lowest = 1000
        for combo in combos:
            value = self.evaluate(combo)
            # When using this function to create sets when we have an extra card, need extra conditions
            if game.round_num < len(self.hand):
                # Need to check that the combination created actually makes sense for the correct number of cards
                value = self.evaluate(combo, drawn=True)
                # If the value is 1, the hand can actually go out because the hand is holding an extra card
                if value == 1:
                    value = 0
                # If the value is 0, need to make sure that it will actually work with one less card
                elif value == 0:
                    combo_copy = combo.copy()
                    long = 0
                    longest = combo_copy[0]
                    for path in combo_copy:
                        if len(path.nodes) > long:
                            longest = path
                    longest.nodes.pop(0)
                    value = self.evaluate(combo_copy)
            if value < lowest:
                lowest = value
                best = combo

        # Check all the paths to see if there are paths that need additional cards to go out
        # If the number of cards not in sets is less than 3, do not need more pairs.
        unmatched = 0
        for path in best:
            if len(path.nodes) == 1:
                unmatched += 1
        for path in best:
            # When to look at paths of length 1. Only look at paths of length 1 when there are enough cards outside
            # of non length 1 paths to make another set and there are no sets that need additional cards
            if len(path.nodes) > 1:
                self.path_tracer(path, needed, game)
            elif len(path.nodes) == 1 and unmatched >= 3:
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
            if run[0] > 3:
                needed.append((suit, run[0]-1, 0))
            if run[len(run)-1] < 13:
                needed.append((suit, run[len(run)-1]+1, 0))
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
    # You need a maximum number of cards in your hand - 1 to go out. Check how many cards are NOT in 3 length sets
    # Check how many cards are NOT in 2 length sets
    def evaluate(self, hand, drawn=False):
        wild = 0
        for path in hand:
            wild += len(path.nodes)
        if drawn:
            wild -= 1
        needed = 0
        for path in hand:
            needed += self.path_eval(path, wild)
        return needed

    def path_eval(self, path, wild):
        value = path.evaluate(wild)
        if value is 0:
            return 0
        needed = 0
        path.fix(wild)
        if len(path.nodes) < 3 and (path.type is hand_graph.SET or path.type is hand_graph.NO_TYPE):
            needed = min(len(path.nodes), abs(3 - len(path.nodes)))
        # If it is a run, calculate how many cards you need to fix the run
        elif value > 0 and path.type is hand_graph.RUN:
            # What is the point of BASE?
            i = BASE
            t_path = path.copy()
            # Checks how many cards are needed by adding jokers until the set can go out
            while t_path.evaluate(wild) != 0:
                joker = hand_graph.Node(('J', 0, i))
                t_path.add_node((joker, -1))
                i += 1
            needed += i - BASE
        return needed
