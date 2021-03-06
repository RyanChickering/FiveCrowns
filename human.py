import player


class Player(player.Player):
    def __init__(self):
        self.CHAR_TO_INT = 49
        self.hand = []
        self.complete = False

    # Prompts a player to pick between the discard pile and the mystery card
    def draw(self, game):
        print("Discard pile {0} [q]".format(game.discard))
        print("Card from deck [w]")
        print(self.hand)
        choices = ['q', 'w']
        choice = input("deck (q) pile (w)")
        while choice not in choices:
            choice = input("deck (q) pile (w)")
        if choice is choices[1]:
            self.hand.append(game.deck.draw())
        else:
            self.hand.append(game.discard)

    # asks the player which card to discard
    def discard(self, game):
        print(self.hand)
        choices = [x for x in range(len(self.hand))]
        print("Select a card 1 through {0}".format(len(self.hand)))
        choice = input("enter a card number")
        choice = ord(choice) - self.CHAR_TO_INT
        while choice not in choices:
            choice = input("enter a valid card number")
        game.discard = self.hand.pop(choice)

    # Looking at the cards in the hand, split them into groups that can go
    # together. present the different groupings as options to be picked.
    # To start, a hand looks like
    # [("spade", "6"), ("heart", "5"), ("heart", "6"), ("diamond", "Ke"), ("star", "4"), ("J", "J"), ("star", "3")]
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
        # Sorts the list numerically
        sorted_hand = sorted(self.hand, key=lambda crd: crd[1])
        curr_val = sorted_hand[0][1]
        curr_cnt = 1
        sets = []
        wild_set = []
        non_set = []
        to_add = []
        # Creates groups of cards that have the same number.
        for card in sorted_hand:
            # Checks for wildcards and adds them to a set to be distributed later
            if card[1] is len(self.hand) or card[1] is 0:
                wild_set.append(card)
            elif card[1] is curr_val:
                curr_cnt += 1
                to_add.append(card)
            else:
                # Only adds things with more than a pair
                if len(to_add) > 1:
                    sets.append(to_add)
                elif len(to_add) is not 0:
                    non_set.append(to_add)
                to_add = [card]
                curr_cnt = 1
                curr_val = card[1]
        sets.append(to_add)
        sets.sort(reverse=True, key=len)
        score = 0
        for group in sets:
            if len(group) < 3:
                if len(wild_set) > 0 and len(group) is 2:
                    group.append(wild_set.pop())
                else:
                    for item in group:
                        score += item[1]
        for item in non_set:
            score += item[0][1]
        print("{0}{1}. Score:{2}".format(sets, non_set, score))