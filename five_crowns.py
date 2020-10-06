import deck
import human
import ai
import RandAI
import random
import hand_graph
import reduce_ai
import better_bogo
import compete_ai


"""
What do we need to run a game of five crowns? Initialize the deck each round to a shuffled state
Keep track of the round to know how many cards to deal out. Need to be able to store the state
of each player's hand. Need to be able to recognize when a hand can go out, might want to provide
some sort of automatic hand sorting to make it more obvious. Need to be able to group up cards into
runs and sets. Recognize wild cards. Players need to be able to discard. What functionality do we want
in the game class versus the player class. Game needs to be able to recognize legitimate hands that can go out

Method summary:
Init initializes the game, with how many players. Each player needs a list to keep track of the cards 
currently in their hand

Main game running needs to:
Deal out the next hand after someone has gone out and everyone got another turn

Keep track of each player's score.

Track which cards are in the discard pile


Player functions that are needed:
Draw, and select if they draw from the deck or the discard pile
Discard after drawing. Determine sets within their hand.
Go out (automatically?) once all cards are put into sets.


"""


class FiveCrowns:
    # Players is a list of players
    def __init__(self, players, test_deck=True):
        self.deck = deck.Deck()
        self.is_out = False
        turn_count = 0
        self.round_num = 0
        if test_deck:
            self.deck.test_deck()
        # Meat and potatoes loop that goes through all the rounds,
        # deals cards, draws cards, discards cards.
        for self.round_num in range(3, 14):
            print("{0}'s round".format(self.round_num))
            self.is_out = False
            self.deal(self.round_num, players, test_deck)
            self.discard_pile = [self.deck.draw()]
            rnd_turn = 0
            while not self.is_out:
                for play in players:
                    if self.deck.isEmpty():
                        self.deck = deck.Deck(random.shuffle(self.discard_pile))
                    play.draw(self)
                    self.discard_pile.append(play.discard(self))
                    if play.complete_hand():
                        self.is_out = True
                turn_count += 1
                rnd_turn += 1
            for play in players:
                if not play.complete:
                    if self.deck.isEmpty():
                        self.deck = deck.Deck(random.shuffle(self.discard_pile))
                    play.draw(self)
                    self.discard_pile.append(play.discard(self))
                    play.score += play.hand_value()
            for play in players:
                print(play.score, end="  ")
            print("Turns: ", rnd_turn)
        for i in range(len(players)):
            print("Player ", i+1, " score:", players[i].score)
        print("Average turns: ", turn_count/11)

    def deal(self, round_num, players, test_deck=True):
        # Resets the hand for the player
        for play in players:
            play.hand = []
        # Deals out new cards from the top of the deck to players
        if test_deck:
            self.deck.test_deck()
        else:
            self.deck.__init__()
        for cards in range(round_num):
            for play in players:
                play.hand.append(self.deck.draw())


if __name__ == "__main__":
    player1 = RandAI.Player()
    player2 = compete_ai.Player()
    player3 = reduce_ai.Player()
    player4 = better_bogo.Player()
    FiveCrowns([player2, player3], test_deck=False)

