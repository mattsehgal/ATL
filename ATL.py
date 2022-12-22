import States as S
import Expressions as E
from Expressions import Exp
from util import parse, TrainGate

CONST = E.CONST
PROP = E.PROP
NEG = E.NEG
DISJ = E.DISJ
CONJ = E.CONJ
IMPL =  E.IMPL
CIRCLE = E.CIRCLE
DIAMOND = E.DIAMOND
SQUARE = E.SQUARE
UNTIL = E.UNTIL
AVOID = E.AVOID  # Not Implemented



# Here's the initial setup of the Train-Gate problem
players = ['t', 'c']

q0 = S.State(['oog'], 't')
q1 = S.State(['oog', 'req'], 'c')
q2 = S.State(['oog', 'grant'], 't')
q3 = S.State(['ig'], 'c')

q0.connect([q0, q1])
q1.connect([q0, q1, q2])
q2.connect([q0, q3])
q3.connect([q0, q3])

all_states = [q0, q1, q2, q3]

# Some examples of the first statement on slide 28 of the reference (Bloisi in bibliography of paper)
#  {0}[]((out_of_gate ^ ~grant) -> {c}[](out_of_gate))
#  where [] represents the square path operator, {A} represents that set A of
#  players is the "protagonist" of the expression
# The Exp instances below are the constituent expressions that build the given expression
#   which is represented by total
true = Exp(True, op=CONST)
oog = Exp('oog')
grant = Exp('grant')
ngrant = Exp(grant, op=NEG)
pand = Exp(oog, ngrant, CONJ)
path = Exp(oog, op=(SQUARE, ['c']))
impl = Exp(pand, path, IMPL)
total = Exp(impl, op=(SQUARE, []))
# This can be accomplished with less effort by using the parse function:
print('_'*31+f'Begin Example'+'_'*31)
expression_str = '{0}[]((oog ^ ~grant) -> {c}[](oog))'
print(f'Expression String:\t{expression_str}')
parsed_total = parse(expression_str) # recreating the expression "total" by using the parser
print(f'Parsed Exp Repr:\t{parsed_total}')
print(f'Total Exp Repr:\t\t{total}')
# You can see that total and parsed_total are equivalent
print(f'Equal: {total == parsed_total}')
print('_'*32+'End Example'+'_'*32+'\n')

# When writing your own expressions as strings, please refer to the docstring below for syntax:
'''Expression String Representation Syntax
    
    Regular Operators:
        Constant    :   "true"
                        "false"
        Proposition :   any string of characters
        Negation    :   ~
        Disjunction :   V
        Conjunction :   ^
        Implication :   ->
        
    Path Quantifiers:
        Players :   {_}
                    {_,...}
                    {} or {0}
                    
        *   If players is parametrized with "0", i.e. "{0}", it will behave
            the same as {} as 0 is the symbol for null.
        *   Path Quantifiers must apply to expressions within parenthesis,
            for example, "{c}[](oog)" is legal but "{c}[]oog" is not.
        
    Temporal Operators:
        Circle  :   @
        Diamond :   <>
        Square  :   []
        Until   :   U
        
        *   Circle, Diamond, and Square apply from the left of an expression, 
            Until is infix.
        *   Temporal Operators must apply to expressions within parenthesis,
            for example, "{c}[](oog)" is legal but "{c}[]oog" is not.
        *   Temporal Operators can only come after Path Quantifiers. 
            Until looks like {_}(exp1) U (exp2). 
            
    _______________________________________________________________________________
    
    Below are examples to assist in expression construction:
    
    Usage Examples:
        Players:              {c,t}[](oog ^ grant)
        Temporal Operators:   {0}_(oog ^ grant)     where _ is [], @, or <>
        Until:                {c}(oog ^ grant) U (oog V grant)
        
    Various Train-Gate Examples:
        *   {0}[]((oog ^ ~grant) -> {c,t}[](oog))
        *   {0}[](oog -> {c,t}<>(ig))
        *   {0}[](oog -> {t}<>(req ^ ({c}<>(grant)) ^ ({c}[](~grant)))'
        *   {0}[](ig -> {c}@(oog))'
'''


def test(exp, states=all_states):
    return [exp.check(i) for i in states]


def is_valid(exp, states):
    if type(exp) is str:
        exp = parse(exp)
    out = True
    for state_res in [exp.check(i) for i in states]:
        out = out and state_res
    return out


if __name__ == '__main__':
    # Below are the Train-Gate Problem examples from Bloisi's slides:
    # *  The formulas can be accessed through TG.examples,
    #    the text descriptions can be accessed through TG.descriptions,
    #    and the state graph can be accessed through TG.states.
    #
    # *  The formulas can be evaluated by a certain property test (i.e., is_valid)
    #    this can be achieved by using TG.print(f=<property_test>) which will evaluate
    #    all formulas in the set against the system of states with the given property test.
    #
    # *  Formulas can be added through TG.add_example(e, t=None) where e is the text
    #    representation of the formula and t is an option text description of the formula.
    TG = TrainGate()
    TG.print(f=test)
    TG.print(f=is_valid)

    # To create your own system and expressions you can create a new State graph
    # in the same way as it is done earlier in this file.
    # Use the Expression String Representation Syntax to create expressions and
    # then use the parse function to get an Exp representation of the expression.
