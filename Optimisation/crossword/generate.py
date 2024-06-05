import sys

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # For Each Variable
        for var in self.domains:
            # For Each Word in the domain of the Variable
            for word in set(self.domains[var]):

                # Remove Word if it does not satisfy the constraint
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Define a variable to store the value True if revision was made
        revised = False

        # Get all Overlaps Between x and y
        overlap = self.crossword.overlaps[x, y]

        # If overlaps exist, make x arc consistent with y
        if overlap is not None:
            i, j = overlap

            # For each word in the domain of Variable x
            for x_word in set(self.domains[x]):

                # Remove the word if no constraint satisfying word is found in the domain of y
                if all(x_word[i] != y_word[j] for y_word in self.domains[y]):
                    self.domains[x].remove(x_word)

                    # Set Revised to true, as the domain of x has been revised
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # If no arcs are provided, then get a list of all arcs (variable pairs)
        if arcs is None:
            arcs = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]

        # Initialize the queue with the list of arcs
        queue = list(arcs)

        # Process arcs until the queue is empty
        while queue:

            # Dequeue an arc from the queue
            (x, y) = queue.pop(0)

            # Revise the domains to make the arc (x, y) consistent
            if self.revise(x, y):

                # If the domain of x is empty after revision, no solution exists
                if not self.domains[x]:
                    return False

                # Enqueue all arcs (z, x) where z is a neighbor of x, excluding y
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        # Return True if arc consistency is enforced and no domains are empty
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        return set(assignment.keys()) == set(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Iterate over each variable and its assigned word in the assignment
        for var, word in assignment.items():
            # Check if the length of the word matches the variable's required length
            if var.length != len(word):
                return False

            # Iterate over each neighbor of the current variable
            for neighbor in self.crossword.neighbors(var):
                # If the neighbor is already assigned
                if neighbor in assignment:

                    # Get the overlap positions between the current variable and the neighbor
                    i, j = self.crossword.overlaps[var, neighbor]
                    # Check if the characters at the overlap positions match
                    if word[i] != assignment[neighbor][j]:
                        return False
        # If all checks are passed, the assignment is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Define a helper function to count the number of values ruled out
        def count_ruled_out(value):
            count = 0
            # Iterate over each neighbor of the variable
            for neighbor in self.crossword.neighbors(var):
                # Only consider neighbors that are not yet assigned
                if neighbor not in assignment:
                    # Get the overlap positions between the variable and the neighbor
                    i, j = self.crossword.overlaps[var, neighbor]
                    # Count how many values in the neighbor's domain are inconsistent with the current value
                    count += sum(
                        1
                        for neighbor_value in self.domains[neighbor]
                        if neighbor_value[j] != value[i]
                    )
            return count

        # Sort the domain of the variable by the number of values they rule out for neighbors
        return sorted(self.domains[var], key=count_ruled_out)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Get a list of variables that are not yet assigned
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # Define a key function for sorting the unassigned variables
        def key_func(var):
            # Return a tuple with the number of remaining values and the negative degree
            # Number of remaining values (len(self.domains[var])) should be minimized
            # Degree (-len(self.crossword.neighbors(var))) should be maximized (hence negative)
            return (len(self.domains[var]), -len(self.crossword.neighbors(var)))

        # Return the unassigned variable that minimizes the key function
        return min(unassigned, key=key_func)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # If the assignment is complete (all variables are assigned), return the assignment
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable using Minimum Remaining Value(MRV) and Degree heuristics
        var = self.select_unassigned_variable(assignment)

        # Iterate over values in the domain of the selected variable, ordered by least constraining value
        for value in self.order_domain_values(var, assignment):

            # Create a new assignment with the selected variable assigned to the current value
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Check if the new assignment is consistent
            if self.consistent(new_assignment):
                # Recursively call backtrack with the new assignment
                result = self.backtrack(new_assignment)

                # If a valid result is found, return it
                if result is not None:
                    return result

        # If no valid assignment is found, return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
