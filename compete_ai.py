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
        for node in graph.nodes:
            # If a card has no edges and is not wild, it is useless
            if len(node.edges) is 0 and not hand_graph.HandGraph.wild_check(node, game.round_num):
                useless.append(node)
            for edge in node.edges:
                if edge[hand_graph.COST_VAL] < game.round_num:
                    break
        if len(useless) > 0 and useless is not None:
            useless.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            return self.node_in_hand(useless.pop())
        else:
            needed = []
            best = self.identify_sets(needed, game)
            worst = 0
            worst_path = hand_graph.Path()
            for path in best:
                if self.path_eval(path, game.round_num) is not 0:
                    value = path.evaluate(game.round_num)
                    if value > worst:
                        worst = value
                        worst_path = path
            worst_path.nodes.sort(key=lambda crd: crd.name[hand_graph.VAL_IDX])
            if len(worst_path.nodes) > 0:
                return self.node_in_hand(worst_path.nodes.pop())
            return self.hand.pop(0)

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
