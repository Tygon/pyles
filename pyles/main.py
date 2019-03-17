import abc
import copy
import sys

sys.setrecursionlimit(100000000)

MAX_DEPTH = 22
MAX_TESTS = 1000000

# Skip 0 and 1 because they are the hashes for True and False
HASH_VALUES = {'AndEq':2, 'OrEq':3, 'NotEq':4, 'ImpliesEq':5, 'BiImpliesEq':6, 'SymbolEq':7, 'Open':8, 'Close':9}

class EquationHistory():
    def __init__(self, eq, description, parent):
        self.eq = eq
        self.description = description
        self.parent = parent
        self.children = []
        self.exhausted = False

        if parent:
            parent.children.append(self)

    def __repr__(self):
        text = ''
        if self.parent:
            text += str(self.parent)
        return text + str(self.eq) + ' by ' + self.description + '\n'

class Equation():
    def __init__(self):
        self._arg_list = []
        self.string = ""
        self.hash = 0

    @property
    def arg1(self):
        return self._arg_list[0]

    @arg1.setter
    def arg1(self, value):
        if len(self._arg_list) < 1:
            self._arg_list.append(value)
        else:
            self._arg_list[0] = value

    @property
    def arg2(self):
        return self._arg_list[1]

    @arg2.setter
    def arg2(self, value):
        if len(self._arg_list) < 2:
            self._arg_list.append(value)
        else:
            self._arg_list[1] = value

    @abc.abstractmethod
    def eval(self):
        raise NotImplementedError

    @abc.abstractmethod
    def sub_str(self):
        raise NotImplementedError
    
    def set_symbol_value(self, symbol, value):
        for x in self._arg_list:
            if isinstance(x, SymbolEq):
                if x.symbol == symbol:
                    x.value = value
                    return True
            elif x.set_symbol_value(symbol, value):
                return True

    def get_symbol_set(self):
        symbol_set = set()
        for x in self._arg_list:
            if isinstance(x, SymbolEq):
                symbol_set.add(x)
            else:
                symbol_set |= x.get_symbol_set()
        
        return symbol_set

    def __eq__(self, other):
        if isinstance(self, type(other)):
            if isinstance(self, SymbolEq):
                return self.symbol == other.symbol
            else:
                return self._arg_list == other._arg_list
        else:
            return False


class AndEq(Equation):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def eval(self):
        return self.arg1.eval() and self.arg2.eval()

    def __repr__(self):
        return '(' + repr(self.arg1) + ' and ' + repr(self.arg2) + ')'

    def sub_str(self):
        return '(' + self.arg1.sub_str() + ' and ' + self.arg2.sub_str() + ')'

    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['Open']) + str(hash(self.arg1)) + str(HASH_VALUES['AndEq']) + str(hash(self.arg2)) + str(HASH_VALUES['Close']))

class OrEq(Equation):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def eval(self):
        return self.arg1.eval() or self.arg2.eval()

    def __repr__(self):
        return '(' + repr(self.arg1) + ' or ' + repr(self.arg2) + ')'

    def sub_str(self):
        return '(' + self.arg1.sub_str() + ' or ' + self.arg2.sub_str() + ')'

    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['Open']) + str(hash(self.arg1)) + str(HASH_VALUES['OrEq']) + str(hash(self.arg2)) + str(HASH_VALUES['Close']))

class ImpliesEq(Equation):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def eval(self):
        if self.arg1.eval() and not self.arg2.eval():
            return False
        else:
            return True

    def __repr__(self):
        return '(' + repr(self.arg1) + ' -> ' + repr(self.arg2) + ')'

    def sub_str(self):
        return '(' + self.arg1.sub_str() + ' -> ' + self.arg2.sub_str() + ')'
    
    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['Open']) + str(hash(self.arg1)) + str(HASH_VALUES['ImpliesEq']) + str(hash(self.arg2)) + str(HASH_VALUES['Close']))

class BiImpliesEq(Equation):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2

    def eval(self):
        if self.arg1.eval() == self.arg2.eval():
            return True
        else:
            return False

    def __repr__(self):
        return '(' + repr(self.arg1) + ' <-> ' + repr(self.arg2) + ')'

    def sub_str(self):
        return '(' + self.arg1.sub_str() + ' <-> ' + self.arg2.sub_str() + ')'

    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['Open']) + str(hash(self.arg1)) + str(HASH_VALUES['BiImpliesEq']) + str(hash(self.arg2)) + str(HASH_VALUES['Close']))

class NotEq(Equation):
    def __init__(self, arg):
        super().__init__()
        self.arg1 = arg

    def eval(self):
        return not self.arg1.eval()

    def __repr__(self):
        return '(not ' + repr(self.arg1) + ')'

    def sub_str(self):
        return '(not ' + self.arg1.sub_str() + ')'
    
    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['Open']) + str(HASH_VALUES['NotEq'])  + str(hash(self.arg1)) + str(HASH_VALUES['Close']))


class SymbolEq(Equation):
    def __init__(self, symbol, value=False):
        super().__init__()
        self.symbol = symbol
        self.value = value

    def eval(self):
        return self.value

    def __repr__(self):
        return self.symbol

    def sub_str(self):
        return str(self.value)

    def __hash__(self):
        return hash(str(self))
        return int(str(HASH_VALUES['SymbolEq']) + str(ord(self.symbol)))

def identity(eq):
    """
    P and True = P
    Q or False = Q
    """
    if isinstance(eq, AndEq):
        if isinstance(eq.arg2, bool):
            if eq.arg2 == True:
                return eq.arg1
    elif isinstance(eq, OrEq):
        if isinstance(eq.arg2, bool):
            if eq.arg2 == False:
                return eq.arg1

def idempotent(eq):
    """
    P and P = P
    Q or Q = Q
    """
    if isinstance(eq, AndEq) or isinstance(eq, OrEq):
        if eq.arg1 == eq.arg2:
            return eq.arg1

def domination(eq):
    """
    P or True = True
    Q and False = False
    """
    if isinstance(eq, AndEq):
        if isinstance(eq.arg2, bool):
            if eq.arg2 == False:
                return False
    elif isinstance(eq, OrEq):
        if isinstance(eq.arg2, bool):
            if eq.arg2 == True:
                return True

def commutative(eq):
    """
    P and Q = Q and P
    P or Q = Q or P
    """
    if isinstance(eq, AndEq):
        return AndEq(eq.arg2, eq.arg1)
    elif isinstance(eq, OrEq):
        return OrEq(eq.arg2, eq.arg1)

def associative(eq):
    """
    (P and Q) and R = P and (Q and R)
    (P or Q) or R = P or (Q or R)
    """
    if isinstance(eq, AndEq) or isinstance(eq, OrEq):
        if isinstance(eq.arg1, type(eq)):
            arg1 = eq.arg1.arg1
            arg2 = type(eq)(eq.arg1.arg2, eq.arg2)

            return type(eq)(arg1, arg2)

def distributive(eq):
    """
    P or (Q and R) = (P or Q) and (P or R)
    P and (Q or R) = (P and Q) or (P and R)
    """
    if isinstance(eq, OrEq):
        if isinstance(eq.arg2, AndEq):
            arg1 = OrEq(eq.arg1, eq.arg2.arg1)
            arg2 = OrEq(eq.arg1, eq.arg2.arg2)

            return AndEq(arg1, arg2)
        elif isinstance(eq.arg1, AndEq) and isinstance(eq.arg2, AndEq) and eq.arg1.arg1 == eq.arg2.arg1:
            arg1 = eq.arg1.arg1
            arg2 = OrEq(eq.arg1.arg2, eq.arg2.arg2)

            return OrEq(arg1, arg2)
    elif isinstance(eq, AndEq):
        if isinstance(eq.arg2, OrEq):
            arg1 = AndEq(eq.arg1, eq.arg2.arg1)
            arg2 = AndEq(eq.arg1, eq.arg2.arg2)

            return OrEq(arg1, arg2)
        elif isinstance(eq.arg1, OrEq) and isinstance(eq.arg2, OrEq) and eq.arg1.arg1 == eq.arg2.arg1:
            arg1 = eq.arg1.arg1
            arg2 = OrEq(eq.arg1.arg2, eq.arg2.arg2)

            return OrEq(arg1, arg2)

def negation(eq):
    """
    P and not P = F
    P or not P = T
    """
    if isinstance(eq, AndEq) and isinstance(eq.arg2, NotEq):
        if eq.arg1 == eq.arg2.arg1:
            return False
    elif isinstance(eq, OrEq) and isinstance(eq.arg2, NotEq):
        if eq.arg1 == eq.arg2.arg1:
            return True

def absorption(eq):
    """
    P and (P or Q) = P
    P or (P and Q) = P
    """
    if isinstance(eq, AndEq) or isinstance(eq, OrEq):
        if isinstance(eq.arg2, AndEq) or isinstance(eq.arg2, OrEq):
            if not isinstance(eq, type(eq.arg2)):
                if eq.arg1 == eq.arg2.arg1:
                    return eq.arg1

def double_negation(eq):
    """
    not not P = P
    P = not not P
    """
    if isinstance(eq, NotEq) and isinstance(eq.arg1, NotEq):
        return eq.arg1.arg1
    # else:
    #     return NotEq(NotEq(eq))

def implication_equivalence(eq):
    """
    P -> Q = not P or Q
    """
    if isinstance(eq, ImpliesEq):
        arg1 = NotEq(eq.arg1)
        arg2 = eq.arg2

        return OrEq(arg1, arg2)
    elif isinstance(eq, OrEq) and isinstance(eq.arg1, NotEq):
        arg1 = eq.arg1.arg1
        arg2 = eq.arg2
        
        return ImpliesEq(arg1, arg2)

def biconditional_equivalence(eq):
    """
    P <-> Q = (P -> Q) and (Q -> P)
    """
    if isinstance(eq, BiImpliesEq):
        arg1 = ImpliesEq(eq.arg1, eq.arg2)
        arg2 = ImpliesEq(eq.arg2, eq.arg1)

        return AndEq(arg1, arg2)
    elif isinstance(eq, AndEq) and isinstance(eq.arg1, ImpliesEq) and isinstance(eq.arg2, ImpliesEq):
        if eq.arg1.arg1 == eq.arg2.arg2 and eq.arg1.arg2 == eq.arg2.arg1:
            arg1 = eq.arg1.arg1
            arg2 = eq.arg1.arg2
            
            return BiImpliesEq(arg1, arg2)

def demorgans_law(eq):
    """
    not (P and Q) = not P or not Q
    not (P or Q) = not P and not Q
    """
    if isinstance(eq, NotEq):
        if isinstance(eq.arg1, AndEq) or isinstance(eq.arg1, OrEq):
            arg1 = NotEq(eq.arg1.arg1)
            arg2 = NotEq(eq.arg1.arg2)

            if isinstance(eq.arg1, AndEq):
                return OrEq(arg1, arg2)
            else:
                return AndEq(arg1, arg2)

    elif isinstance(eq, AndEq) or isinstance(eq, OrEq):
        if isinstance(eq.arg1, NotEq) and isinstance(eq.arg2, NotEq):
            arg1 = eq.arg1.arg1
            arg2 = eq.arg2.arg1
            
            if isinstance(eq, AndEq):
                return NotEq(OrEq(arg1, arg2))
            else:
                return NotEq(AndEq(arg1, arg2))


FUNC_LIST = [identity, idempotent, domination, commutative, associative, distributive, negation, absorption, double_negation, demorgans_law] #, implication_equivalence, biconditional_equivalence]

def get_depth(eq):
    if isinstance(eq, SymbolEq):
        return 1
    elif not isinstance(eq, Equation):
        return 0

    sum = 0
    for x in eq._arg_list:
        sum += get_depth(x)
    
    return sum + 1

def copy_eq(eq):
    # return copy.deepcopy(eq)
    if isinstance(eq, NotEq):
        return NotEq(copy_eq(eq.arg1))
    elif isinstance(eq, AndEq):
        return AndEq(copy_eq(eq.arg1), copy_eq(eq.arg2))
    elif isinstance(eq, OrEq):
        return OrEq(copy_eq(eq.arg1), copy_eq(eq.arg2))
    elif isinstance(eq, ImpliesEq):
        return ImpliesEq(copy_eq(eq.arg1), copy_eq(eq.arg2))
    elif isinstance(eq, BiImpliesEq):
        return BiImpliesEq(copy_eq(eq.arg1), copy_eq(eq.arg2))
    elif isinstance(eq, SymbolEq):
        return eq
    else:
        return eq


def get_variations(func, eq):
    """
    Gets all the variations of an equation when a function is applied.
    Function is applied to main eq and all of its arguments.
    Does not mix variations of eq AND its arguments as that is two operations.

    :param func: Identity function to apply to eq.
    :param eq: Equation to modify.
    :returns: List of Eq objects.
    """
    
    variation_list = []
    if not isinstance(eq, SymbolEq) and isinstance(eq, Equation):
        # Apply to main eq
        new_eq = func(eq)
        if new_eq and get_depth(new_eq) <= MAX_DEPTH:
            variation_list.append(new_eq)
        
        # Apply to all arguments
        for i, arg in enumerate(eq._arg_list):
            if not isinstance(arg, SymbolEq) and isinstance(arg, Equation):
                # Recursively get all variations of arg
                arg_var_list = get_variations(func, arg)
                if arg_var_list:
                    for var in arg_var_list:
                        # Create new eq and change its variable
                        new_eq = copy_eq(eq)
                        new_eq._arg_list[i] = var

                        if get_depth(new_eq) <= MAX_DEPTH:
                            variation_list.append(new_eq)
                            
    return variation_list

def prove(eq1, eq2, simplify=False):
    # tested_list = [hash(eq1)]
    tested_list_str = {str(eq1)}

    # eq2_hash = hash(eq2)
    eq2_str = str(eq2)
    
    top_node = EquationHistory(eq1, 'start', None)
    search_list = [top_node]

    curr_history = top_node

    while True:
        for func in FUNC_LIST:
            variation_list = get_variations(func, curr_history.eq)
            for var in variation_list:
                # var_hash = hash(var)
                var_str = str(var)

                if var == True:
                    print('true')

                if var_str == eq2_str or (simplify and (isinstance(var, bool) or isinstance(var, SymbolEq))):
                    print('finished', len(search_list))
                    return EquationHistory(var, str(func), curr_history)
                elif var_str not in tested_list_str:
                    # for i, x in enumerate(tested_list):
                    #     if var_hash == x:
                    #         print(var_str, 'same hash as', tested_list_str[i])

                    # tested_list.append(var_hash)
                    tested_list_str.add(var_str)

                    new_hist = EquationHistory(var, str(func), curr_history)
                    search_list.append(new_hist)

                    if simplify and len(tested_list_str) > MAX_TESTS:
                        print('max tests')
                        return top_node

                    if len(tested_list_str) % 100000 == 0:
                        print(len(tested_list_str))

        del search_list[0]
        if len(search_list) > 0:
            curr_history = search_list[0]
        else:
            if simplify:
                print('list empty', len(tested_list_str))
                return top_node
            else:
                raise Exception("Proof failed.")

def parse_text(text):
    parse_list = []
    open_count = 0
    sub = ''
    for c in text:
        if c == '(':
            if open_count >= 1:
                sub += c
            open_count += 1
        elif c == ')':
            if open_count >= 1:
                sub += c
            open_count -= 1

            if open_count == 0:
                parse_list.append(parse_text(sub))
                sub = ''

        elif open_count > 0:
            sub += c
        elif c == ' ':
            new_word = True
        else:
            if len(parse_list) == 0 or new_word:
                parse_list.append(c)
                new_word = False
            else:
                parse_list[len(parse_list) - 1] += c
    
    return parse_list

def parse_equation(parse_list, symbol_list=[]):
    if len(parse_list) == 0:
        return parse_list[0]

    for i, x in enumerate(parse_list):
        if isinstance(x, list):
            parse_list[i] = parse_equation(x, symbol_list)

    if len(parse_list) == 0:
        return parse_list[0]

    for i, x in enumerate(parse_list):
        if x == 'True':
            parse_list[i] = True
        elif x == 'False':
            parse_list[i] = False
        elif x not in ('not', 'and', 'or', '->', '<->') and not isinstance(x, Equation):
            if x in (sym.symbol for sym in symbol_list):
                parse_list[i] = next(sym for sym in symbol_list if sym.symbol == x)
            else:
                parse_list[i] = SymbolEq(x)
                symbol_list.append(parse_list[i])
    
    while 'not' in parse_list:
        for i, x in enumerate(parse_list):
            if x == 'not':
                parse_list[i] = NotEq(parse_list[i + 1])
                parse_list[i + 1] = None
                break
            
        parse_list = list(filter(None, parse_list))

    if len(parse_list) == 0:
        return parse_list[0]
    
    while 'and' in parse_list:
        for i, x in enumerate(parse_list):
            if x == 'and':
                parse_list[i] = AndEq(parse_list[i - 1], parse_list[i + 1])
                parse_list[i - 1] = None
                parse_list[i + 1] = None
                break
        
        parse_list = list(filter(None, parse_list))

    if len(parse_list) == 0:
        return parse_list[0]
    
    while 'or' in parse_list:
        for i, x in enumerate(parse_list):
            if x == 'or':
                parse_list[i] = OrEq(parse_list[i - 1], parse_list[i + 1])
                parse_list[i - 1] = None
                parse_list[i + 1] = None
                break
        
        parse_list = list(filter(None, parse_list))

    while '->' in parse_list:
        for i, x in enumerate(parse_list):
            if x == '->':
                parse_list[i] = ImpliesEq(parse_list[i - 1], parse_list[i + 1])
                parse_list[i - 1] = None
                parse_list[i + 1] = None
                break
        
        parse_list = list(filter(None, parse_list))

    while '<->' in parse_list:
        for i, x in enumerate(parse_list):
            if x == '<->':
                parse_list[i] = BiImpliesEq(parse_list[i - 1], parse_list[i + 1])
                parse_list[i - 1] = None
                parse_list[i + 1] = None
                break
        
        parse_list = list(filter(None, parse_list))

    return parse_list[0]

def get_top_history(eq_history):
    top_history = eq_history
    while eq_history.parent:
        top_history = top_history.parent
    
    return top_history

def get_lowest_depth(eq_history, lowest_depth):
    lowest_per_child = []
    for child in eq_history.children:
        lowest_per_child.append(get_lowest_depth(child, lowest_depth))

    lowest = eq_history
    for child in lowest_per_child:
        if get_depth(child.eq) < get_depth(lowest.eq):
            lowest = child
    return lowest

def simplify(eq):
    proof = prove(eq, None, True)
    return get_lowest_depth(proof, None)

def get_equation(text):
    return parse_equation(parse_text(text))

def main():
    # eq = get_equation("not (((X or ((not x) and not (Z or Y))) and (not Z)) or (Y and (Z and (not X))))")
    # variation_list = get_variations(commutative, eq)
    # print(variation_list)

    # print(hash(get_equation("(((a or (b -> c)) or (b or (not a))) and ((c or (not a)) or (a or ((not b) or c))))")))

    # eq1 = get_equation("not (((X or ((not x) and not (Z or Y))) and (not Z)) or (Y and (Z and (not X))))")
    # print(type(eq1))
    # eq2 = get_equation("((Z and X) or ((Y and X) and Z)) or (((Y or Z) and not (Z and Y)) and not X)")

    # print(hash(eq1), hash(eq2))
    # print(hash(eq1) == hash(eq2))

    # proof = prove(eq1, eq2)
    # print('proof')
    # print(proof)

    # eq1 = parse_equation(parse_text("s <-> ((w -> a) and (not a))"))

    # proof = prove(eq1, True)

    # print('proof')
    # print(proof)

    # print('simplify')
    # print(simplify(eq2))

    # eq1 = get_equation("(not (((X or ((not X) and (not (Z or Y)))) and (not Z)) or (Y and (Z and (not X)))))")
    # eq2 = get_equation("(((Z and X) or ((Y and X) and Z)) or (((Y or Z) and (not (Z and Y))) and (not X)))")

    eq1 = get_equation("((not ((Z and (not X)) and Y)) and (((not X) and Y) or Z))")
    eq2 = get_equation("(((not (X or (Y and Z))) and (Z or Y)) or (X and Z))")

    print(prove(eq1, eq2))

if __name__ == "__main__":
    main()
    
