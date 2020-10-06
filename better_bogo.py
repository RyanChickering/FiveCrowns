import player
import hand_graph
import random
import compete_ai

"""
The better bogo represents a player with the bare minimum of skill. They can recognize when they have sets and won't
throw them away, but they will still draw at random and throw away their non-safe cards at random.

Effectively a downgraded version of compete_ai

"""


class Player(compete_ai.Player):
    # Draws a random card
    def draw(self, game):
        choice = random.randint(0, 1)
        if choice is 0:
            self.hand.append(game.deck.draw())
        else:
            self.hand.append(game.discard_pile.pop())

    # Discards a random card not in a complete set
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
