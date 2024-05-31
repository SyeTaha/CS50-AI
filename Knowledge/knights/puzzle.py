from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


def XOR(prop1, prop2):
    '''
    
    Define a function to Return exclusice OR

    '''
    # Either Proposition 1 or 2 and not Both
    return And(Or(prop1, prop2), Not(And(prop1, prop2)))


# Puzzle 0
# A says "I am both a knight and a knave."
A_Statement_p0 = And(AKnight, AKnave)

knowledge0 = And(
    # A is a Knight or Knave, both not Both
    XOR(AKnave, AKnight),

    And(Or(AKnave, AKnight), Not(And(AKnave, AKnight))),
    Implication(AKnave, Not(A_Statement_p0)),
    Implication(AKnight, A_Statement_p0)
)


# Puzzle 1
# A says "We are both knaves."
A_Statement_p1 = And(AKnave, BKnave)

# B says nothing.


knowledge1 = And(
    # A is a Knight or Knave, both not Both
    XOR(AKnight, AKnave),
    # B is a Knight or Knave, both not Both
    XOR(BKnight, BKnave),

    # If A is a Knave, then A's Statement is not true
    Implication(AKnave, Not(A_Statement_p1)),
    Implication(AKnight, A_Statement_p1)
)

# Puzzle 2
# A says "We are the same kind."
A_Statement_p2 = Or(And(AKnave, BKnave), And(AKnight, BKnight))

# B says "We are of different kinds."
B_Statement_p2 = Not(Or(And(AKnave, BKnave), And(AKnight, BKnight)))  # ~((A and B) or (~A and ~B))

knowledge2 = And(

    # A is a Knight or Knave, both not Both
    XOR(AKnight, AKnave),
    # B is a Knight or Knave, both not Both
    XOR(BKnight, BKnave),

    # If A is a Knave, then A's Statement is not true
    Implication(AKnave, Not(A_Statement_p2)),
    Implication(AKnight, A_Statement_p2),

    # If B is a Knave, then B's Statement is not true
    Implication(BKnave, Not(B_Statement_p2)),
    Implication(BKnight, B_Statement_p2),

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
A_Statement_p3 = Or(AKnight, AKnave)

# B says "A said 'I am a knave'."
B_Statement1_p3 = Implication(A_Statement_p3, AKnave)

# B says "C is a knave."
B_Statement2_p3 = CKnave

# C says "A is a knight."
C_Statement_p3 = AKnight

knowledge3 = And(
    # A is a Knight or Knave, both not Both
    XOR(AKnight, AKnave),
    # B is a Knight or Knave, both not Both
    XOR(BKnight, BKnave),
    # C is a Knight or Knave, both not Both
    XOR(CKnight, CKnave),

    # If A is a Knave, then A's Statement is not true
    Implication(AKnave, Not(A_Statement_p3)),
    Implication(AKnight, A_Statement_p3),

    # If B is a Knave, then both of B's Statement are not true
    Implication(BKnave, Not((And(B_Statement1_p3, B_Statement2_p3)))),
    Implication(BKnight, (And(B_Statement1_p3, B_Statement2_p3))),

    # If C is a Knave, then C's Statement is not true
    Implication(CKnave, Not(C_Statement_p3)),
    Implication(CKnight, C_Statement_p3)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
