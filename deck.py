# Class that makes the deck for a game of Five Crowns
# Deck is a double deck that includes cards 3-K in 5 suits and 6 jokers
# Has methods to shuffle the deck and to draw the top card from the deck.

import random


class Deck:
    # Initializes the 116 card deck in a sorted order
    def __init__(self):
        suits = ["club", "spade", "diamond", "heart", "star"]
        cards = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
        # Adds the normal 110 cards to the deck
        self.deck = [(s, c) for s in suits for c in cards for x in range(2)]
        # Adds the six jokers to the deck
        for j in range(6):
            self.deck.append(("J", 0))
        self.shuffle()

    # Removes the top card from the deck. Returns a tuple of ("suit", "denom")
    def draw(self):
        return self.deck.pop()

    # Puts the deck into a shuffled order
    def shuffle(self):
        random.shuffle(self.deck)

    def test_deck(self):
        self.deck = [('star', 9), ('J', 0), ('spade', 7), ('diamond', 10), ('club', 11), ('heart', 8),
                     ('heart', 3), ('star', 10), ('heart', 10)]
