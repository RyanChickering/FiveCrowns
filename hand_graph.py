class Path:
    def __init__(self):
        self.type = -1
        self.cost = 0
        self.nodes = []

    def add_node(self, edge):
        self.cost += edge[1]
        self.nodes.append(edge[0])

    def __str__(self):
        output = ''
        for node in self.nodes:
            output += str(node.__str__())
        """output += " cost: " + str(self.cost)
        if self.type is SET:
            output += " type: set"
        elif self.type is RUN:
            output += " type: run"
        else:
            output += " type: no type"""""
        return output

    def copy(self):
        new_path = Path()
        new_path.type = self.type
        new_path.cost = self.cost
        new_path.nodes = self.nodes.copy()
        return new_path

    # Fixes runs to have the proper cost
    def fix(self, wild):
        if self.type is not RUN:
            return
        self.nodes.sort(reverse=False, key=lambda edg: edg.name[VAL_IDX])
        # Sets the start of the run
        curr = self.nodes[0].name[VAL_IDX] - 1
        j = 0
        while j < len(self.nodes) and HandGraph.wild_check(self.nodes[j], wild, draw=False):
            j += 1
        if j == len(self.nodes):
            print(self)
            j -= 1
        curr = self.nodes[j].name[VAL_IDX] - 1
        self.cost = 0
        for node in self.nodes:
            if node.name[VAL_IDX] == wild or node.name[SUIT_IDX] == 'J':
                self.cost -= 1
            else:
                self.cost += node.name[COST_VAL] - curr - 1
                curr = node.name[VAL_IDX]

    # Function used for ordering in the fix function
    def fix_func(self, node):
        return node.name[VAL_IDX]

    # Evaluates the number of points in an incomplete run. Out controls whether the game is out, as wild cards should
    # not be counted as points until the game is over
    # If you have 3 cards in a run that go together and 1 that doesn't quite stretch yet, only count the one without
    # the stretch
    def evaluate(self, wild, out=False, fits_hand=True):
        valid = True
        cost = 0
        if len(self.nodes) < 3:
            valid = False
        elif self.type is RUN:
            # fixes runs to have the correct cost
            # go through the run, looking at each node. if you have 3 in a row that go together, do not count those
            # against the hand. Save the longest stretch of run? Keep score, if you get three in a row, get rid of the
            # score for the last three. If the next one is part of the run, don't add score. Could have disjoint runs
            # of three in the same much larger run.
            self.fix(wild)
            if self.cost > 0:
                valid = False
        # add up the points found in non-valid groupings
        valid = valid and fits_hand
        if not valid:
            if self.type is RUN:
                # want to identify runs of three in a row or more
                # move through nodes, every time you hit a hole, make a new path using the nodes up until that point
                # find how many wild cards you have. Then you know the distance that you can jump
                wilds = []
                unused = []
                for node in self.nodes:
                    if HandGraph.wild_check(node, wild, draw=False):
                        wilds.append(node)
                    else:
                        unused.append(node)
                curr = unused[0]
                prev_nodes = []
                path = [curr.name[VAL_IDX]]
                # separates the run into smaller paths.
                wild_count = len(wilds)
                prev_node = 0
                valid = True
                p_cost = 0
                for j in range(1, len(unused)):
                    # if in the range allowed by the wildcards
                    if unused[j].name[VAL_IDX] <= curr.name[VAL_IDX] + wild_count + 1:
                        # decrease wild value by the number of skipped cards
                        if (unused[j].name[VAL_IDX] - curr.name[VAL_IDX] + 1) > 0:
                            prev_node = j
                        wild_count -= unused[j].name[VAL_IDX] - curr.name[VAL_IDX] + 1
                        # if we need a wild card, these cards are not safe
                        if wild_count != len(wilds):
                            valid = False
                        p_cost += curr.name[VAL_IDX]
                    else:
                        p_cost += curr.name[VAL_IDX]
                        if valid and len(path) > 3:
                            p_cost = 0
                        valid = True
                        prev_nodes.append([path, p_cost])
                        p_cost = 0
                        wild_count = len(wilds)
                        if j > prev_node + 1:
                            j = prev_node
                        path = []

                    path.append(unused[j].name[VAL_IDX])
                    curr = unused[j]
                if len(path) > 0:
                    if valid and len(path) > 3:
                        p_cost = 0
                    else:
                        p_cost += unused[len(unused)-1].name[VAL_IDX]
                    prev_nodes.append([path, p_cost])
                # sorts the sets by their total cost
                prev_nodes.sort(reverse=True, key=lambda i_path: i_path[1])
                cost = 0
                # looks at the highest cost run that can be fixed and counts the nodes that weren't used in that run
                to_count = unused.copy()
                for i_path in prev_nodes:
                    if len(i_path[0]) + len(wilds) >= 3:
                        for val_idx in i_path[0]:
                            for node in unused:
                                if val_idx == node.name[VAL_IDX]:
                                    if to_count.__contains__(node):
                                        to_count.remove(node)
                                        break
                        break
                for node in to_count:
                    cost += node.name[VAL_IDX]
            else:
                for node in self.nodes:
                    if node.name[VAL_IDX] == wild:
                        if out:
                            cost += 20
                        else:
                            cost += 0
                    elif node.name[SUIT_IDX] == 'J':
                        if out:
                            cost += 50
                        else:
                            cost += 0
                    else:
                        cost += node.name[VAL_IDX]
        return cost


class Node:
    def __init__(self, name=""):
        self.name = name
        self.edges = []

    def __str__(self):
        return self.name


VAL_IDX = 1
SUIT_IDX = 0
COST_VAL = 1
DECK_IDX = 2
SET_VAL = -2
WILD_VAL = -1
SET = 0
RUN = 1
NODE = 0
NO_TYPE = -1


class HandGraph:
    def __init__(self):
        self.nodes = []
        self.hand = []

    # the cost to move between two nodes in a run is the absolute difference between them -1
    # the cost to use a wildcard is -1
    # the cost to move between two nodes in a set is -2.
    # A loop with non-negative cost cannot bring in negative edges and a loop with negative cost
    # cannot bring in non-negative edges.
    # Look for every path that goes through at least three nodes and has either a cost of 0
    # or a cost of < -2
    # An edge is a tuple consisting of a node and a cost

    def find_edges(self, hand, drawn=False):
        self.hand = hand
        # Turn all of the cards into nodes
        for card in hand:
            new_card = Node(name=card)
            self.nodes.append(new_card)

        wilds = []
        for node in self.nodes:
            if self.wild_check(node, len(hand), drawn):
                wilds.append(node)

        # For each card, check what cards it can connect to
        for node in self.nodes:
            wild = False
            if (node.name[VAL_IDX] is len(hand) - 1 and drawn) or (node.name[VAL_IDX] is len(hand) and not drawn)\
                    or node.name[SUIT_IDX] == 'J':
                wild = True
            for check in self.nodes:
                # Check for self
                if not (check.name[VAL_IDX] is node.name[VAL_IDX] and check.name[SUIT_IDX] is node.name[SUIT_IDX] \
                        and node.name[DECK_IDX] is check.name[DECK_IDX]):
                    # Check for wildcard
                    # If we are looking for edges on a hand that has just drawn, they have an extra card so wildcard is
                    # 1 less than the length of their hand.
                    if drawn and check.name[VAL_IDX] is len(hand)-1:
                        node.edges.append((check, WILD_VAL))
                    elif not drawn and check.name[VAL_IDX] is len(hand):
                        node.edges.append((check, WILD_VAL))
                    elif check.name[SUIT_IDX] is "J":
                        node.edges.append((check, WILD_VAL))
                    # Check for the same number
                    # Wild check so that wild cards only have edges to other wild cards
                    elif node.name[VAL_IDX] is check.name[VAL_IDX] and not wild:
                        node.edges.append((check, SET_VAL))
                    # Check for the same suit
                    elif node.name[SUIT_IDX] is check.name[SUIT_IDX] and not wild:
                        distance = abs(node.name[VAL_IDX] - check.name[VAL_IDX])-1
                        if (distance < len(hand) and not drawn) or (distance < len(hand) - 1 and drawn):
                            node.edges.append((check, distance))

    # OUTDATED METHOD
    # To check for a complete hand, try to make it so that every node in the graph belongs to a valid subgraph of size
    # at least 3. To do this, start by checking that each node is at least connected to something. Will need a fix for
    # the current wild card system.
    # Option 2: Build the longest path for the first card. Using the remaining cards, try to build the longest path for
    # the next card that is not currently in a valid path. If no such path exists, go back to a previous path and look
    # for an alternative. Repeat until there are either no alternatives or a success is found.
    # This might be a constraints problem
    # If you fail with the unused nodes, try with all the nodes. If still no path exists, fail. If a path exists,
    # reserve those nodes as used and go back and try to build a new path for earlier cards not using the now reserved
    # cards. At some point, need to have an exit condition for repeated failure.
    # This method is heavily flawed and needs to be looked into. Currently use all_combo and evaluation functions to
    # determine when a hand has 0 points
    def complete_hand(self, hand):
        self.find_edges(hand)
        unused_nodes = []
        reserved_nodes = []
        for node in self.nodes:
            unused_nodes.append(node)
        while len(unused_nodes) > 0:
            # check if all of the unused nodes are wild cards. If they are, we can go out.
            if len(unused_nodes[0].edges) is 0:
                return False
            else:
                # Generates the longest path possible with the available nodes
                new_sub_graph = self.sub_graph(unused_nodes[0], unused_nodes)
                # Checks if the subgraph was valid, and if it was removes the cards used from the available pile
                if len(new_sub_graph.nodes) >= 3:
                    for sg_node in new_sub_graph.nodes:
                        if reserved_nodes.__contains__(sg_node):
                            return False
                        if unused_nodes.__contains__(sg_node):
                            unused_nodes.remove(sg_node)
                # If the path was NOT valid, check conditions to see if a valid path could be made
                else:
                    # If even using all the nodes a valid length path could not be made, return false
                    if len(unused_nodes) is len(self.nodes):
                        return False
                    longest_sub_graph = self.sub_graph(unused_nodes[0], self.nodes)
                    if len(longest_sub_graph.nodes) < 3:
                        return False
                    # If a valid path COULD be made, reserve those nodes and try again.
                    else:
                        for card in longest_sub_graph.nodes:
                            if reserved_nodes.__contains__(card):
                                return False
                            else:
                                reserved_nodes.append(card)
                        unused_nodes = self.nodes
        # If every node was able to be used, the hand can go out.
        return True

    # Check whether the input card (a node) is wild
    @staticmethod
    def wild_check(card, length, draw=False):
        if card.name[VAL_IDX] == length and not draw:
            return True
        elif card.name[VAL_IDX] == length - 1 and draw:
            return True
        elif card.name[SUIT_IDX] == 'J':
            return True
        else:
            return False

    # Creates every possible combination of cards possible for a hand
    # No longer used and has minor bugs where it misses combinations
    def comprehensive_combo(self, hand, draw=False):
        self.find_edges(hand, drawn=draw)
        unused_nodes = []
        # Semi-sorts the nodes so that all cards are looked at before the wild cards.
        for node in self.nodes:
            if self.wild_check(node, len(self.nodes), draw):
                unused_nodes.append(node)
            else:
                unused_nodes.insert(0, node)
        curr_hand = []
        combinations = []
        return self.all_combinations(unused_nodes[0], -1, unused_nodes, curr_hand, combinations, draw=draw)

    # This method returns a list of hands that have been organized into all possible arrangements
    # For every node, explore every valid neighbor. Move through using only unused nodes.
    # Argument explanation: node is the current card node, which is a list containing a value and a cost
    # cost is the cost of the node being added from the previous node
    # unused_nodes is the unused nodes for the current recursion
    # curr_hand is a list of the paths that can be made in the current recursion
    # combinations is a list of all the possible hands
    # path is the current path being built. If no path is provided, it will create a new path
    # draw indicates whether the hand currently holds an extra card
    def all_combinations(self, node, cost, unused_nodes, curr_hand, combinations, path=None, draw=False):
        if path is None:
            path = Path()
        # Add a type to the path if applicable
        # Need to avoid c5 W W d8 r8 being valid
        if cost == -1 and path.type is NO_TYPE:
            path.type = NO_TYPE
        elif cost < -1:
            path.type = SET
        elif cost >= 0:
            path.type = RUN
        # add the new node to the path. I don't think the cost in the path is necessary
        path.add_node((node, cost))
        unused_nodes.remove(node)
        # When we run out of unused nodes, add the hand to the combinations and end
        if len(unused_nodes) is 0:
            curr_hand.append(path)
            combinations.append(curr_hand)
        else:
            neighbors = node.edges
            # Verify that the neighbors are valid to be added to the current path
            new_neighbors = []
            for neighbor in neighbors:
                # Check that nodes are unused and are correct for the type of path
                if unused_nodes.__contains__(neighbor[NODE]):
                    # Sets can have other set neighbors or wild cards added
                    if path.type is SET:
                        if neighbor[COST_VAL] <= -1:
                            new_neighbors.append(neighbor)
                    # Runs can have other run neighbors or wild cards added
                    # don't want to add the same number to a run twice
                    elif path.type is RUN:
                        new = True
                        for node in new_neighbors:
                            if node[VAL_IDX] == neighbor[NODE].name[VAL_IDX]:
                                new = False
                        for node in path.nodes:
                            if node.name[VAL_IDX] == neighbor[NODE].name[VAL_IDX]:
                                new = False
                        if neighbor[COST_VAL] >= 0 and new:
                            new_neighbors.append(neighbor)
                    # If the path doesn't have a set yet, any neighbor can be added
                    else:
                        new_neighbors.append(neighbor)
            # If there are no valid neighbors, add the path to hand and start a new path in the hand
            if len(new_neighbors) == 0:
                curr_hand.append(path)
                self.all_combinations(unused_nodes[0], -1, unused_nodes, curr_hand, combinations, draw=draw)
            # End the current path and start a new one
            elif len(unused_nodes) > 0:
                new_hand = curr_hand.copy()
                new_hand.append(path.copy())
                self.all_combinations(unused_nodes[0], -1, unused_nodes.copy(), new_hand, combinations,
                                      draw=draw)
            # For each valid neighbor, add it to the path and explore what the hand looks like
            for neighbor in new_neighbors:
                # Repeat for the new node
                self.all_combinations(neighbor[NODE], neighbor[COST_VAL], unused_nodes.copy(),
                                      curr_hand.copy(), combinations, path.copy(), draw)

        return combinations

    # Create the largest set group and largest run group such that every card is used in their longest version of each
    # of these. Having done this, chop up the different paths and put them together to create only the useful
    # combinations and hopefully operate a lot faster than generating every combination
    def all_combo(self, hand, draw=False):
        combinations = []
        self.find_edges(hand)
        wilds = []
        unused = []
        for node in self.nodes:
            if self.wild_check(node, len(self.nodes), draw=draw):
                wilds.append(node)
            else:
                unused.append(node)
        sets_free = unused.copy()
        runs_free = unused
        set_paths = []
        run_paths = []
        while len(sets_free) > 0:
            set_paths.append(self.sub_graph(sets_free.pop(), sets_free, True))
        while len(runs_free) > 0:
            run_paths.append(self.sub_graph(runs_free.pop(), runs_free, False))
        # Using all these max length paths, try to put them together in all the different ways that you can
        # Build a list of overlapped nodes so we know where we need to split
        # conflicts contains list of tuples containing pairs of conflicting paths and the conflicting node. Lists of
        # conflicts contain one run path and however many conflicting set paths that it crosses
        # conflicts are nodes that have a name and a list of other conflicts that they are in conflict with
        conflicts = []
        removals = []
        # One run can contain multiple set contributing cards
        for r_path in run_paths:
            overlap = None
            for s_path in set_paths:
                conflict = self.compare_paths(s_path, r_path)
                if conflict is not None:
                    remove = False
                    # Remove run paths of length 1 if they are covered in a different path
                    if len(r_path.nodes) == 1 and len(s_path.nodes) > 1:
                        removals.append(r_path)
                        remove = True
                    if len(s_path.nodes) == 1:
                        removals.append(s_path)
                        remove = True
                    if not remove:
                        r_new = True
                        s_new = True
                        for conflict in conflicts:
                            if conflict.name is r_path:
                                conflict.edges.append(s_path)
                                r_new = False
                            if conflict.name is s_path:
                                conflict.edges.append(r_path)
                                s_new = False
                        if r_new:
                            overlap = Node(name=r_path)
                            overlap.edges.append(s_path)
                            conflicts.append(overlap)
                        if s_new:
                            overlap = Node(name=s_path)
                            overlap.edges.append(r_path)
                            conflicts.append(overlap)
        # Remove length 1 paths
        while len(removals) > 0:
            curr = removals.pop()
            if run_paths.__contains__(curr):
                run_paths.remove(curr)
            if set_paths.__contains__(curr):
                set_paths.remove(curr)
        # Removes paths that had conflicts from the list of paths
        for over in conflicts:
            if run_paths.__contains__(over.name):
                run_paths.remove(over.name)
            for item in over.edges:
                if set_paths.__contains__(item):
                    set_paths.remove(item)
        # if there were no conflicts, return the only reasonable combination of paths
        if len(conflicts) == 0:
            curr_hand = []
            for path in set_paths:
                curr_hand.append(path)
            for path in run_paths:
                curr_hand.append(path)
            combinations.append(curr_hand)
            if len(wilds) > 0:
                wild_combination = []
                self.wild_distribute(0, combinations[0], wild_combination, wilds.copy())
                return wild_combination
            return combinations
        # if there were conflicts, return every combination of reasonable paths
        # for every conflict, need to create two versions of the hand, one where the set gets the conflict and one
        # where the run gets the conflict. Add all the paths without conflicts and then sort out the conflicts.
        # create combinations where wildcards are doled out at the end
        # Need to keep track of the free nodes, when adding in the conflict sets, delete nodes that aren't free out of
        # the path.
        curr_hand = []
        for path in run_paths:
            curr_hand.append(path)
        for path in set_paths:
            curr_hand.append(path)
        # need to run through the conflicts in all possible orders.
        # splits the conflicts into two different lists, one for conflicts with two or more connected to it and one
        # for conflicts with only one related conflict
        multi = []
        singles = []
        for conflict in conflicts:
            if len(conflict.edges) >= 2:
                multi.append(conflict)
            else:
                singles.append(conflict)
        # If a conflict is connected to a single conflict which is also then only connected to the original conflict,
        # only want one instance of that conflict in singles
        # Singles who are only connected to a single, need to be added in before the single checking stage
        c_singles = []
        u_singles = []
        for single in singles:
            unique = True
            for single2 in u_singles:
                if self.compare_paths(single.name, single2.edges[0]) is not None:
                    unique = False
                    break
            if unique:
                u_singles.append(single)

        # create all the permutations of the list of conflicts
        permutations = []
        self.factorial_sort(multi, len(multi), len(multi), permutations)
        if len(u_singles) > 0:
            for permutation in permutations:
                for single in u_singles:
                    permutation.append(single)
        # Adds the single conflict conflicts into the different permutations which creates all the ones that we want
        permutations = self.add_singles(singles, permutations)

        # processes the conflicts such that every node is only used once in each combination
        combinations = self.combine(permutations)
        if len(run_paths) > 0 or len(set_paths) > 0:
            for combin in combinations:
                for run_path in run_paths:
                    combin.append(run_path)
                for set_path in set_paths:
                    combin.append(set_path)

        # creates the different combinations allowed by available wildcards
        if len(wilds) > 0:
            wild_combinations = []
            for combination in combinations:
                self.wild_distribute(0, combination, wild_combinations, wilds.copy())
            return wild_combinations
        else:
            return combinations

    def add_singles(self, singles, permutations):
        for single in singles:
            new_perms = []
            for permutation in permutations:
                # find the conflict and create two new permutations and add them to the new_permutations list
                # When the conflict is found, copy the current permutation and make a version where the single is
                # processed before it's conflict and one where it is processed after its conflict
                for conflict in permutation:
                    con = self.compare_paths(conflict.name, single.name)
                    if con is not None:
                        alt_perm = permutation.copy()
                        alt_perm.insert(0, single)
                        permutation.append(single)
                        new_perms.append(alt_perm)
                        new_perms.append(permutation)
                        break
            permutations = new_perms.copy()
        return permutations

    # creates new combinations where wildcards are added in all possible orders to paths in a combination
    def wild_distribute(self, n, combination, combinations, wilds):
        # if called and there are no wild cards remaining, append the current combination and end the exploration
        if len(wilds) == 0:
            combinations.append(combination)
            return
        # if we are on the last path in the combination and there are still wildcards left, need to add them all to that
        # path and then add the combination to the total combinations
        elif n == len(combination)-1:
            path = combination.pop(n)
            path = path.copy()
            combination.insert(n, path)
            for wild in wilds:
                path.nodes.append(wild)
            combinations.append(combination)
            return
        # start different combinations
        elif n < len(combination)-1:
            while len(wilds) > 0:
                self.wild_distribute(n + 1, combination.copy(), combinations, wilds.copy())
                path = combination.pop(n)
                path = path.copy()
                combination.insert(n, path)
                path.nodes.append(wilds.pop())
            combinations.append(combination)
            return

    # given a list, the size of the list, and the original size of the list, will output all the permutations to the
    # permutations list provided
    def factorial_sort(self, conflicts, size, n, permutations):
        if size == 0:
            permutations.append(conflicts.copy())
            return

        for i in range(size):
            self.factorial_sort(conflicts, size - 1, n, permutations)
            if size % 2 == 1:
                temp = conflicts[0]
                conflicts[0] = conflicts[size - 1]
                conflicts[size - 1] = temp
            else:
                temp = conflicts[i]
                conflicts[i] = conflicts[size - 1]
                conflicts[size - 1] = temp

    def factorial(self, num):
        values = [1, 1, 2, 6, 24, 120]
        if num > 5:
            return num * self.factorial(num-1)
        else:
            return values[num]

    # Takes the permuatations of the orders of conflicts, and resolves them by only using unused nodes from each
    # path
    def combine(self, permutations):
        combinations = []
        for permutation in permutations:
            used_nodes = []
            combination = []
            for conflict in permutation:
                temp = conflict.name.copy()
                for node in conflict.name.nodes:
                    if used_nodes.__contains__(node):
                        temp.nodes.remove(node)
                    else:
                        used_nodes.append(node)
                if len(temp.nodes) > 0:
                    combination.append(temp)
            combinations.append(combination)
        return combinations


    # Method that removes nodes that have been used from a path and removes new nodes from the free_nodes
    def remove_used(self, path, free_nodes):
        new_path = path.copy()
        # Go through the nodes in the path and remove the ones that have been used and mark ones that haven't been
        # used as now used.
        for node in path.nodes:
            if not free_nodes.__contains__(node):
                new_path.nodes.remove(node)
            else:
                free_nodes.remove(node)
        return new_path

    # method that returns the node shared by two paths if any
    def compare_paths(self, path1, path2):
        for node in path1.nodes:
            if path2.nodes.__contains__(node):
                return node
        return None

    # Generates the largest valid subgraph that it can for the node using the remaining nodes.
    # Node indicates the card to start the path from. Free_nodes indicates the nodes available to use in the set.
    # path indicates the currently progressing path. Allow_any indicates whether the path cost needs to be valid or not
    # Have wild cards sucked up ahead of time and distributed after the paths are made
    def sub_graph(self, node, free_nodes, sets, path=None):
        if path is None:
            path = Path()
        path.nodes.append(node)
        neighbors = node.edges
        wildcards = []
        for edge in neighbors:
            # Check if we have not yet used the neighbor
            if free_nodes.__contains__(edge[NODE]):
                # Check if the node is a wildcard. If it is, add it to wildcards
                if edge[NODE].name[SUIT_IDX] is 'J' or edge[NODE].name[VAL_IDX] is len(self.hand):
                    wildcards.append(edge)
                if sets:
                    if edge[COST_VAL] == SET_VAL:
                        path.type = SET
                        path.add_node(edge)
                        free_nodes.remove(edge[NODE])
                else:
                    # may need to check that the run doesn't already contain the same number
                    new = True
                    for node in path.nodes:
                        if node.name[VAL_IDX] == edge[NODE].name[VAL_IDX]:
                            new = False
                    if edge[COST_VAL] >= 0 and new:
                        path.type = RUN
                        path.add_node(edge)
                        free_nodes.remove(edge[NODE])
                        for item in edge[NODE].edges:
                            if item[COST_VAL] > -1:
                                neighbors.append(item)
        return path

    # Returns a score for a hand grouping.
    # A hand if a list of paths
    @staticmethod
    def evaluate_hand(hand, drawn=False, out=False):
        wild = 0
        cost = 0
        # Determines the wild card value
        for path in hand:
            wild += len(path.nodes)
        if drawn:
            wild -= 1
        for path in hand:
            cost += path.evaluate(wild, out)
        return cost

    # Evaluates every combination of hands returned by all_combo and returns the lowest score possible for the current
    # hand
    @staticmethod
    def evaluate_hands(combos, drawn=False, out=False):
        lowest = 1000
        for comb in combos:
            value = HandGraph.evaluate_hand(comb, drawn=drawn, out=out)
            if value < lowest:
                lowest = value
        return lowest

    # Checks for wild cards but using the tuple format used by the deck
    @staticmethod
    def wild_check_tuple(card, length, draw=False):
        if card[VAL_IDX] == length and not draw:
            return True
        elif card[VAL_IDX] == length - 1 and draw:
            return True
        elif card[SUIT_IDX] == 'J':
            return True
        else:
            return False

# Main method for testing different functions
if __name__ == "__main__":
    test_hand = [('s', 11, 0), ('d', 10, 0), ('s', 3, 0)]
    # r 10 r 10 r 8 r 8 d 8 d 9 c 9 d 9 r 6 r 7 r 5
    # (r 5 r 6 r 7) (
    # [('r', 6, 0), ('r', 5, 1), ('r', 7, 1), ('c', 11, 0), ('r', 11, 1), ('d', 8, 0), ('r', 8, 0), ('r', 10, 0), ('d', 9, 0), ('J', 0, 1), ('r', 10, 1)]
    graph = HandGraph()
    """
    
    path = Path()
    path.add_node((('J', 0, 1), -1))
    path.add_node((('J', 0, 2), -1))
    path.add_node((('r', 5, 1), -1))
    print(path.evaluate(3, out=True))

    
    numbers = [1, 2, 3, 4]
    permutations = []
    graph.factorial_sort(numbers, len(numbers), len(numbers), permutations)
    for permutation in permutations:
        print(permutation)
    """

    all_combos = graph.all_combo(test_hand, False)
    # all_combos = graph.comprehensive_combo(test_hand, False)
    low = 1000
    high = 0
    i = 0
    for combo in all_combos:
        i += 1
        val = graph.evaluate_hand(combo, out=True)
        if val < low:
            low = val
        if val > high:
            high = val
        for group in combo:
            print(group, end=' ')
        print(val)
    print("Number of combinations: ", len(all_combos))
    print("Highest scoring hand: ", high)
    print("Lowest scoring hand: ", low)
        


    """
    [('c', 7, 0), ('s', 4, 0), ('c', 6, 1), ('c', 6, 0)]
10's round
[('r', 5, 0), ('r', 6, 1), ('r', 7, 1), ('c', 11, 0), ('r', 11, 1), ('d', 8, 0), ('r', 8, 0), ('r', 10, 0), ('d', 9, 0), ('c', 10, 1)]
11's round
[('h', 3, 1), ('s', 4, 1), ('c', 10, 0), ('r', 4, 1), ('c', 9, 1), ('h', 11, 1), ('r', 3, 0), ('h', 4, 1), ('r', 11, 0), ('r', 4, 0), ('c', 12, 0)]
12's round
[('s', 6, 1), ('s', 7, 1), ('c', 6, 0), ('d', 8, 1), ('h', 8, 0), ('s', 7, 0), ('c', 7, 1), ('r', 12, 0), ('d', 6, 0), ('s', 7, 0), ('s', 7, 1), ('d', 6, 1)]"""

