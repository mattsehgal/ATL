from States import GREEN

# v3: avoid and diamond

# Operator constants
CONST = -1
PROP = 0
NEG = 1
DISJ = 2
CONJ = 3
IMPL = 4
CIRCLE = 5
SQUARE = 6
UNTIL = 7
AVOID = 8
DIAMOND = 9

# Index constants
OP = 0
PLAYERS = 1


class Exp:
    # assuming all operators are binary (can nest with parenthesis)
    #  when op==CONST, PROP, NEG, CIRCLE, SQUARE only subexp1 has value
    #  if op is combined path/temporal, then it's a 2-iterable of type and players (in the path quantifier)
    def __init__(self, subexp1, subexp2=None, op=PROP):
        self.subexp1 = subexp1
        self.subexp2 = subexp2
        self.op = op

    def __repr__(self):
        if type(self.op) is int:
            if self.op is CONST:
                return '{}'.format(self.subexp1)
            elif self.op is PROP:
                return '{}'.format(self.subexp1)
            elif self.op is NEG:
                return '~{}'.format(self.subexp1.__repr__())
            elif self.op is DISJ:
                return '({} V {})'.format(self.subexp1.__repr__(), self.subexp2.__repr__())
            elif self.op is CONJ:
                return '({} ^ {})'.format(self.subexp1.__repr__(), self.subexp2.__repr__())
            elif self.op is IMPL:
                return '({} -> {})'.format(self.subexp1.__repr__(), self.subexp2.__repr__())
        elif self.op[OP] == CIRCLE:
            s = f'({self.subexp1.__repr__()})' if self.subexp1.__repr__()[0] != '(' else self.subexp1.__repr__()
            p = ','.join(self.op[PLAYERS])
            return '{{{}}}@{}'.format(p if p else 0, s)
        elif self.op[OP] == SQUARE:
            s = f'({self.subexp1.__repr__()})' if self.subexp1.__repr__()[0] != '(' else self.subexp1.__repr__()
            p = ','.join(self.op[PLAYERS])
            return '{{{}}}[]{}'.format(p if p else 0, s)
        elif self.op[OP] == UNTIL:
            s1 = f'({self.subexp1.__repr__()})' if self.subexp1.__repr__()[0] != '(' else self.subexp1.__repr__()
            s2 = f'({self.subexp2.__repr__()})' if self.subexp2.__repr__()[0] != '(' else self.subexp2.__repr__()
            p = ','.join(self.op[PLAYERS])
            return '{{{}}}{} U {}'.format(p if p else 0, s1, s2)
        elif self.op[OP] == DIAMOND:
            s = f'({self.subexp2.__repr__()})' if self.subexp2.__repr__()[0] != '(' else self.subexp2.__repr__()
            p = ','.join(self.op[PLAYERS])
            return '{{{}}}<>{}'.format(p if p else 0, s)
        else:
            return self.op

    def __eq__(self, other):
        if not isinstance(other, Exp):
            return False
        if self.op != other.op:
            return False
        if self.subexp1 != other.subexp1:
            return False
        if self.subexp2 != other.subexp2:
            return False
        return True

    # This handles the vast majority of the computational model checking
    def check(self, state):
        if type(self.op) is int:  # that means that it's a simple predicate-order operator
            if self.op == CONST:
                return self.subexp1
            elif self.op == PROP:
                return self.subexp1 in state.props
            elif self.op == NEG:
                return not self.subexp1.check(state)
            elif self.op == DISJ:
                return self.subexp1.check(state) or self.subexp2.check(state)
            elif self.op == IMPL:
                return (not self.subexp1.check(state)) or self.subexp2.check(state)
            else:  # self.op == CONJ:
                return self.subexp1.check(state) and self.subexp2.check(state)

        else:  # it's some path quantifier with players (NOTE: assuming each node has 1 player controlling it)
            if self.op[OP] == CIRCLE:
                # if the expression player isn't controlling, then check if every connection has subexp1
                nearest = [self.subexp1.check(s) for s in state.connections]

                if not (state.player in self.op[PLAYERS]):
                    out = True
                    for i in nearest:
                        out = out and i
                    return out

                # check if any immediate connection has subexp1
                out = False
                for i in nearest:
                    out = out or i
                return out
            elif self.op[OP] == SQUARE:
                # if one of op[PLAYER] is in control, check if they *can* get subexp1 to be true somewhere
                # else check if all options result in subexp1 to be true (other players can't stop subexp1)

                if state.color == GREEN:
                    return True
                state.fill()

                state_res = [self.check(i) for i in state.connections]  # Check if the pathing continues fine
                imm_check = [self.subexp1.check(i) for i in
                             state.connections]  # Check if the subexp is met in all neighboring states

                # Check for if the controlling player *can* make the subexp true
                out = False
                if state.player in self.op[PLAYERS]:
                    for i in range(len(state.connections)):
                        out = out or (state_res[i] and imm_check[i])
                    state.clear()
                    return out
                # Check if the other player(s) can make the subexp false (or, check if they can't avoid making it true)
                else:
                    out = True
                    for i in range(len(state.connections)):
                        out = out and (state_res[i] and imm_check[i])
                    state.clear()
                    return out

            elif self.op[OP] == UNTIL:
                # if subexp2 is true, then you're good
                # if op[PLAYER] is in control, check if they *can* get subexp2 to be true following subexp1

                if self.subexp2.check(state):
                    return True  # found subexp2
                elif state.color == GREEN:
                    return False  # ran out of states without finding subexp2

                state.fill()

                state_res = [self.check(i) for i in state.connections]
                if state.player in self.op[PLAYERS]:
                    out = False
                    for i in state_res:
                        out = out or i
                    state.clear()
                    return out
                else:
                    out = True
                    for i in state_res:
                        out = out and i
                    state.clear()
                    return out

            elif self.op[OP] == AVOID:  # assuming that avoid is avoiding existence of a path
                return Exp(Exp(Exp(self.subexp1, op=NEG), op=(SQUARE, self.op[PLAYERS])), op=NEG).check(state)

            elif self.op[OP] == DIAMOND:
                return Exp(Exp(True, op=CONST), self.subexp1, UNTIL).check(state)