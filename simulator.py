import five_crowns
import RandAI
import compete_ai
import reduce_ai
import better_bogo

if __name__ == "__main__":
    player1 = RandAI.Player("Random", output="random.csv")
    player2 = compete_ai.Player("Compete", output="compete.csv")
    player3 = reduce_ai.Player("Reduce", output="reduce.csv")
    player4 = better_bogo.Player("Better Bogo", output="better_bogo.csv")
    five_crowns.FiveCrowns([player1, player2, player3, player4],
                           output_data="data.csv", output_scores="scores.csv", output_hands=True, print_out=True)
