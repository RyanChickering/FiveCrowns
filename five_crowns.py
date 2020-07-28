import deck
import player


"""
What do we need to run a game of five crowns? Initialize the deck each round to a shuffled state
Keep track of the round to know how many cards to deal out. Need to be able to store the state
of each player's hand. Need to be able to recognize when a hand can go out, might want to provide
some sort of automatic hand sorting to make it more obvious. Need to be able to group up cards into
runs and sets. Recognize wild cards. Players need to be able to discard. What functionality do we want
in the game class versus the player class. Game needs to be able to recognize legitimate hands that can go out

Method summary:
Init initalizes the game, with how many players. Each player needs a list to keep track of the cards 
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
    def __init__(self, players):
        self.deck = deck.Deck()
        self.discard = self.deck.draw()
        # Meat and potatoes loop that goes through all the rounds,
        # deals cards, draws cards, discards cards.
        # TODO: scoring
        for round_num in range(3, 13):
            is_out = False
            self.deal(round_num, players)
            while not is_out:
                for play in players:
                    play.draw(self)
                    play.discard(self)
                    if play.complete_hand:
                        is_out = True
            for play in players:
                if not play.complete_hand:
                    play.draw(self)
                    play.discard(self)

    def deal(self, round_num, players):
        # Resets the hand for the player
        for play in players:
            play.hand = []
        # Deals out new cards from the top of the deck to players
        self.deck.__init__()
        for cards in range(round_num):
            for play in players:
                play.hand.append(self.deck.draw())


if __name__ == "__main__":
    player1 = player.Player()
    player2 = player.Player()
    FiveCrowns([player1, player2])

