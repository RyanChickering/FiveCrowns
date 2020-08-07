"""
Player functions that are needed:
Draw, and select if they draw from the deck or the discard pile
Discard after drawing. Determine sets within their hand.
Go out (automatically?) once all cards are put into sets.
"""

import hand_graph


class Player:
    def __init__(self):
        self.CHAR_TO_INT = 49
        self.hand = []
        self.complete = False

    def draw(self, game):
        raise NotImplementedError("Subclass must implement")

    def discard(self, game):
        raise NotImplementedError("Subclass must implement")

    def complete_hand(self):
        graph = hand_graph.HandGraph()
        self.complete = graph.complete_hand()
        return self.complete

