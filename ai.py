import player
import hand_graph


class Player(player.Player):
    def draw(self, game):
        self.hand.append(game.discard)

    def discard(self, game):
        choice = 0
        game.discard = self.hand.pop(choice)

    def most_useless_card(self):
        return 0

    def build_groups(self):
        graph = hand_graph.HandGraph()

    def determine_need(self):
        return 2
