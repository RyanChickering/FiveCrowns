"""
Player functions that are needed:
Draw, and select if they draw from the deck or the discard pile
Discard after drawing. Determine sets within their hand.
Go out (automatically?) once all cards are put into sets.


"""

import charIO

class Player:
    def __init__(self):
        self.hand = []

    def draw(self, game):
        print("Discard pile {0} [q]".format(game.discard))
        print("Card from deck [w]")
        print(self.hand)
        choices = ['q', 'w']
        choice = charIO.getch()
        while choice not in choices:
            choice = charIO.getch
        if choice is choices[0]:
            self.hand.append(game.deck.draw)
        else:
            self.hand.append(game.discard)

    def discard(self, game):
        print(self.hand)
        choices = [x for x in range(len(self.hand))]
        print("Select a card 1 through {0}".format(1, len(self.hand)+1))
        choice = charIO.getch()
        choice = ord(choice) - 48
        while choice not in choices:
            choice = charIO.getch
        game.discard = self.hand.pop(choice)

    # Looking at the cards in the hand, split them into groups that can go
    # together. present the different groupings as options to be picked.
    # To start, a hand looks like
    # [("spade", "6"), ("heart", "5"), ("heart", "6"), ("diamond", "K"), ("star", "4"), ("J", "J"), ("star", "3")]
    # This hand could be grouped in a few different ways
    # [[("spade", "6"), ("heart", "6"), ("J", "J")], [("star", "4"), ("star", "3")], [("heart", "5")],  [("diamond", "K")]]
    # [[("heart", "5"), ("heart", "6"), ("J", "J")], [("star", "4"), ("star", "3")], [("spade", "6")],  [("diamond", "K")]]
    # [[("heart", "5"), ("heart", "6")], [("star", "4"), ("star", "3"), ("J", "J")], [("spade", "6")], [("diamond", "K")]]
    # Step 1: sort by number.
    # Step 2: Look if you have multiple of the same number
    # Step 3: Look if you have consecutive numbers of the same suit.
    # Step 4: Look if you have numbers 1 away of the same suit
    # Step ?: Look for wildcards and mark them as wildcards.
    # Attempt to arrange options so that the option with the lowest points is listed first.
    def pick_sets(self):
        return True

    def card_val(self, e):
        return e[1]

    def complete_hand(self):
        for group in self.hand:
            if group.len() < 3:
                return False
        return True

