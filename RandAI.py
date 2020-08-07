"""
What would happen if someone playing the game had NO IDEA how to play?
A robot player that performs random draws and discards based on no information
"""

import player
import random


class Player(player.Player):
    def draw(self, game):
        choice = random.randint(0, 1)
        if choice is 0:
            self.hand.append(game.deck.pop())
        else:
            self.hand.append(game.discard)

    def discard(self, game):
        choice = random.randint(0, len(self.hand)-1)
        game.discard = self.hand.pop(choice)
