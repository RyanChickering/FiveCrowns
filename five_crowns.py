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
    def __init__(self, players, test_deck=True, output_hands=None):
        self.deck = deck.Deck()
        self.is_out = False
        turn_count = 0
        self.round_num = 0
        if test_deck:
            self.deck.test_deck()
        if output_hands is not None:
            output_hands = open(output_hands, "a")
        # Meat and potatoes loop that goes through all the rounds,
        # deals cards, draws cards, discards cards.
        for self.round_num in range(3, 14):
            print("{0}'s round".format(self.round_num))
            self.is_out = False
            self.deal(self.round_num, players, test_deck)
            self.discard_pile = [self.deck.draw()]
            rnd_turn = 0
            while not self.is_out:
                # Need the first person of each round to rotate as the deal rotates
                j = 0
                while j < len(players):
                    j += 1
                    i = (self.round_num%len(players) + j) % len(players)
                    if self.deck.isEmpty():
                        self.deck = deck.Deck(random.shuffle(self.discard_pile))
                    players[i].draw(self)
                    self.discard_pile.append(players[i].discard(self))
                    if output_hands is not None:
                        output_hands.write(players[i].hand_string())
                        output_hands.write(" ")
                        output_hands.write(self.card_to_string(self.discard_pile[len(self.discard_pile)-1]))
                    if players[i].complete_hand():
                        self.is_out = True
                        if output_hands is not None:
                            output_hands.write(str(players[i].hand_value()))
                        break
                turn_count += 1
                rnd_turn += 1
                if output_hands is not None:
                    output_hands.write("\n")
            j = 0
            while j < len(players):
                j += 1
                i = (self.round_num % len(players) + j) % len(players)
                if not players[i].complete:
                    if self.deck.isEmpty():
                        self.deck = deck.Deck(random.shuffle(self.discard_pile))
                    players[i].draw(self)
                    self.discard_pile.append(players[i].discard(self))
                    players[i].score += players[i].hand_value()
                    if output_hands is not None:
                        output_hands.write(players[i].hand_string())
                        output_hands.write(" ")
                        output_hands.write(str(players[i].hand_value()))
                        output_hands.write("\n")
            for play in players:
                print(play.score, end="  ")
            print("Turns: ", rnd_turn)
        for play in players:
            print(play.name, " score:", play.score)
        if output_hands is not None:
            output_hands.close()
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

    def card_to_string(self, card):
        out_string = "('"
        out_string += card[hand_graph.SUIT_IDX]
        out_string += "', "
        out_string += str(card[hand_graph.VAL_IDX])
        out_string += ", "
        out_string += str(card[hand_graph.DECK_IDX])
        out_string += ") "
        return out_string


if __name__ == "__main__":
    player1 = RandAI.Player("Random")
    player2 = compete_ai.Player("Compete")
    player3 = reduce_ai.Player("Reduce")
    player4 = better_bogo.Player("Better Bogo")
    FiveCrowns([player2, player3, player4], test_deck=False, output_hands="hand_output")

