# Class that makes the deck for a game of Five Crowns
# Deck is a double deck that includes cards 3-K in 5 suits and 6 jokers
# Has methods to shuffle the deck and to draw the top card from the deck.

import random


class Deck:
    # Initializes the 116 card deck in a sorted order
    def __init__(self, deck=None):
        suits = ["c", "s", "d", "h", "r"]
        cards = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
        # Adds the normal 110 cards to the deck
        if deck is None:
            self.deck = [(s, c, d) for s in suits for c in cards for d in range(2)]
        else:
            self.deck = deck
        # Adds the six jokers to the deck
        for j in range(6):
            self.deck.append(("J", 0, j))
        self.shuffle()

    # Removes the top card from the deck. Returns a tuple of ("suit", "denom", deck)
    def draw(self):
        return self.deck.pop()

    # Puts the deck into a shuffled order
    def shuffle(self):
        random.shuffle(self.deck)

    def isEmpty(self):
        return len(self.deck) == 0

    def test_deck(self):
        """self.deck = [('r', 9, 0), ('c', 11, 0), ('r', 5, 0), ('r', 7, 0), ('s', 8, 1), ('s', 8, 0),
                     ('d', 8, 0), ('r', 12, 0)]"""
        self.deck = [('c', 7, 1) , ('d', 3, 0), ('c', 7, 1), ('d', 6, 1), ('s', 12, 1)]
