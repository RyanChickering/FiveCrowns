"""
An AI strategy whose main goal is to reduce the number of points in their hand.
If the card on the top of the pile can save points, they will take it. Discards the highest card in the hand that isn't
safe.

"""


import player
import hand_graph

SUIT_IDX = 0
VAL_IDX = 1
DECK_IDX = 2


class Player(player.Player):
    def __init__(self, name):
        self.name = name
        self.CHAR_TO_INT = 49
        self.hand = []
        self.complete = False
        self.score = 0
        self.pitch = None

    def draw(self, game):
        self.pitch = None
        # Need to decide between the discard or the deck
        # If the discard will reduce the hand's score, need to take it
        # Easiest to code way would be to sim drawing the card, then discarding each card in the hand until you had the
        # lowest score for each possible discard. If there was a lower score, take it and throw out the card we didn't
        # need
        sim_hand = self.hand.copy()
        graph = hand_graph.HandGraph()
        lowest = self.hand_value()
        # Adds the top of the discard pile to the hand for temporary simulation
        temp_pick = game.discard_pile.pop()
        sim_hand.append(temp_pick)
        # Finds the current value of the hand, want to stay below that
        self.pitch = self.pick_worst(sim_hand, game, lowest)
        # If a better hand couldn't be made with the discard pile draw, put it back and pick a random card
        game.discard_pile.append(temp_pick)
        if self.pitch is None:
            self.hand.append(game.deck.draw())
        else:
            self.hand.append(game.discard_pile.pop())

    def discard(self, game):
        # If we picked up from the discard pile, we already know what to get rid of
        if self.pitch is not None:
            return self.hand.pop(self.pitch)
        # Evaluates the current hand for the worst card to carry
        self.pitch = self.pick_worst(self.hand, game, 1000)
        return self.hand.pop(self.pitch)

    def pick_worst(self, hand, game, lowest):
        pitch = None
        for i in range(len(hand)):
            graph = hand_graph.HandGraph()
            sim_hand = hand.copy()
            sim_hand.pop(i)
            combos = graph.all_combo(sim_hand, draw=False)
            # Check all the combinations for a hand with the discarded card picked
            for combo in combos:
                value = hand_graph.HandGraph.evaluate_hand(combo, out=game.is_out)
                # Keep track of the lowest bet.
                if value < lowest:
                    lowest = value
                    pitch = i
        return pitch
