import deck
import hand_graph


if __name__ == "__main__":
    reps = 200
    output = open("avg_hand_data", 'w')
    for round_num in range(3, 14):
        round_total = 0
        for j in range(reps):
            t_deck = deck.Deck()
            hand = []
            for i in range(0, round_num):
                hand.append(t_deck.draw())
            graph1 = hand_graph.HandGraph()
            combos = graph1.all_combo(hand, draw=False)
            round_total += graph1.evaluate_hands(combos, drawn=False, out=True)
        out_string = str(round_num) + ", " + str(round_total/reps) + "\n"
        output.write(out_string)
    output.close()
