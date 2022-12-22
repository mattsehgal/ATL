import Expressions as E
import States as S
from Expressions import Exp
import re
# v5, handles constants and diamond, handles missing parens, implements a class to encompass the Train-Gate problem

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
            Until looks like {_}(exp1 U exp2).
        
        
    
'''


def tokenize(text):
    return re.findall(r'[()~^vU@]|\[\]|<>|\{.*?\}|->|true|false|\w+', text)


def neg_if_nec(expression, operator_stack):
    # preempts future negation
    if operator_stack and operator_stack[-1] == '~':
        operator_stack.pop()
        return Exp(expression, op=E.NEG)
    else:
        return expression


def construct_expression(subexpressions, operators, op_table):
    expression = None
    while subexpressions:
        sub1 = subexpressions.pop()
        sub2 = subexpressions.pop() if subexpressions else None
        op = operators.pop() if operators else None
        if operators:
            subexpressions.append(Exp(sub1, sub2, op=op_table[op]) if op and sub2 else sub1)
        else:
            expression = Exp(sub1, sub2, op=op_table[op]) if op and sub2 else sub1
    return expression


def hacky_leftover_parse(estack, ostack, otable):
    e = []
    o = []
    while ostack:
        op = ostack.pop()
        if op == '$':
            e.append(neg_if_nec(estack.pop(), ostack))
        elif op in otable:
            o.append(op)
    # construct expression from sub expressions
    return construct_expression(e, o, otable)


def parse(text):
    op_table = {'~': E.NEG, '^': E.CONJ, 'V': E.DISJ, '->': E.IMPL, }  # operator lookup table
    temp_op_table = {'#': E.SQUARE, '[]': E.SQUARE, '@': E.CIRCLE, 'U': E.UNTIL, '<>': E.DIAMOND}  # temporal operator lookup table
    exp_stack = []  # expression stack
    op_stack = []  # operator stack
    quant_stack = []  # path quantifier and temporal operator stack

    for token in tokenize(text):
        if token == 'true' or token == 'false':
            val = True if token == 'true' else False
            exp_stack.append(Exp(val, op=E.CONST))
            op_stack.append('$')
        # Left Parenthesis
        elif token == '(':
            op_stack.append(token)
        # Right Parenthesis: end of expression
        elif token == ')':
            curr_ops = []  # constituent operator stack
            curr_exps = []  # constituent expression stack
            op = op_stack.pop()
            # iterate to start of expression
            while op != '(':
                # push expression to constituent expressions stack
                if op == '$':
                    curr_exps.append(neg_if_nec(exp_stack.pop(), op_stack))
                # push operator to constituent operators stack
                elif op in op_table:
                    curr_ops.append(op)
                op = op_stack.pop()
            # construct expression from sub expressions
            exp_stack.append(construct_expression(curr_exps, curr_ops, op_table))
            # apply path quantifiers and temporal operators
            if op_stack and op_stack[-1] in temp_op_table:
                tempop = quant_stack.pop()
                if tempop != E.UNTIL and tempop != E.DIAMOND:  # Circle or Square
                    exp_stack.append(Exp(exp_stack.pop(), op=(tempop, quant_stack.pop())))
                    op_stack.pop()
                    if op_stack[-1] == '%':
                        op_stack.pop()
                else:  # Diamond or Until
                    sub2 = exp_stack.pop()
                    if tempop == E.DIAMOND:
                        # {A}<>Exp == {A}true U exp
                        sub1 = Exp(True, op=E.CONST)
                        tempop == E.UNTIL
                    else:
                        sub1 = exp_stack.pop()
                    exp_stack.append(Exp(sub1, sub2, op=(tempop, quant_stack.pop())))
                    # strip operators left of subexp1
                    if op_stack[-1] == 'U':
                        op_stack.pop()  # remove U
                        if op_stack[-1] == '$':
                            op_stack.pop()  # remove $
                            if op_stack[-1] == '%':
                                op_stack.pop()  # remove %
                                continue

            # push expression symbol to operator stack
            op_stack.append('$')
        # Operator
        elif token in op_table:
            op_stack.append(token)
            if token == 'U':
                quant_stack.append(op_table[token])
        # Path Quantifier
        elif token[0] == '{':
            token = [] if token[1:len(token) - 1] == '0' else token[1:len(token) - 1].split(',')
            quant_stack.append(token)
            op_stack.append('%')
        # Temporal Operator
        elif token in temp_op_table:
            quant_stack.append(temp_op_table[token])
            op_stack.append(token if token != '[]' else '#')
        # Proposition
        else:
            exp_stack.append(Exp(token))
            op_stack.append('$')

    if op_stack:  # handles leftover symbols caused by missing parens
        exp_stack.append(hacky_leftover_parse(exp_stack, op_stack, op_table))

    return exp_stack.pop()


# Wrapper for the Train-Gate Problem and examples from the Bloisi slides
class TrainGate:
    def __init__(self):
        self.players = ['c', 't']
        q0 = S.State(['oog'], 't')
        q1 = S.State(['oog', 'req'], 'c')
        q2 = S.State(['oog', 'grant'], 't')
        q3 = S.State(['ig'], 'c')
        q0.connect([q0, q1])
        q1.connect([q0, q1, q2])
        q2.connect([q0, q3])
        q3.connect([q0, q3])
        self.states = [q0, q1, q2, q3]

        t1 = 'Whenever the train is out of the gate and does not have a grant to enter the gate, ' \
             'the controller can prevent it from entering the gate.'
        ex1 = '{0}[]((oog ^ ~grant) -> {c,t}[](oog))'
        t3 = 'Whenever the train is out of the gate, the train and the controller' \
             'can cooperate so that the train will enter the gate.'
        ex3 = '{0}[](oog -> {c,t}<>(ig))'
        t4 = 'Whenever the train is out of the gate, it can eventually request a grant for entering the gate, ' \
             'in which case the controller decides whether the grant is given or not.'
        ex4 = '{0}[](oog -> {t}<>(req ^ ({c}<>(grant)) ^ ({c}[](~grant)))'
        t5 = 'Whenever the train is in the gate, the controller can force it out in the next step.'
        ex5 = '{0}[](ig -> {c}@(oog))'
        self.descriptions = [t1, t3, t4, t5]
        self.examples = list(map(parse, [ex1, ex3, ex4, ex5]))

    def eval(self, f, e=None, s=None):
        return f(e, s)

    def print(self, f):
        import textwrap
        for ex, t in zip(self.examples, self.descriptions):
            print(f'"{textwrap.fill(t, width=75)}"\n'
                  f'Expression:\t{ex}\n'
                  f'{f.__name__}:\t{self.eval(f, ex, s=self.states)}\n')

    def add_example(self, e, t=None):
        self.examples.append(parse(e))
        self.descriptions.append(t if t else 'No text for example.')
