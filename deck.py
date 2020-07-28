import random

class Deck:
    # Initializes the 116 card deck in a sorted order
    def __init__(self):
        suits = ["club", "spade", "diamond", "heart", "star"]
        cards = {"3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"}
        # Adds the normal 110 cards to the deck
        self.deck = [(s, c) for s in suits for c in cards]
        # Adds the six jokers to the deck
        for j in range(6):
            self.deck.append(("J", "J"))
        self.shuffle()

    # Removes the top card from the deck. Returns a tuple of ("suit", "denom")
    def draw(self):
        return self.deck.pop()

    # Puts the deck into a shuffled order
    def shuffle(self):
        random.shuffle(self.deck)

