import copy
import sys

from .equation import Equation, AndEq, OrEq, NotEq, ImpliesEq, BiImpliesEq, SymbolEq
from .identities import FUNC_LIST
from .database import SetDatabase

sys.setrecursionlimit(100000000)

DEFAULT_MAX_DEPTH = 22
DEFAULT_MAX_TESTS = 1000000


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


def get_variations(func, eq, max_depth=DEFAULT_MAX_DEPTH):
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
        if new_eq and get_depth(new_eq) <= max_depth:
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

                        if get_depth(new_eq) <= max_depth:
                            variation_list.append(new_eq)
                            
    return variation_list

def prove(eq1, dest_eq, database=SetDatabase(), simplify=False, max_depth=DEFAULT_MAX_DEPTH, max_tests=DEFAULT_MAX_TESTS):
    """
    Attempts to prove that eq1=eq2 through logical equivalences.
    Performs a breadth-first search.

    :param eq1: Equation that will be modified.
    :param dest_eq: Destination equation.
    :param database: Database to keep track of tested equations.
    :param simplify: If true, function will not stop until MAX_TESTS reached or all variations have been checked.
    :param max_depth: Max depth of variations to check.
    :param max_tests: Max amount to equations to test. ONLY works when simplify=True.

    :returns: An equation history obj. The matching equation if found, otherwise the top equation.
    """
    dest_eq_str = str(dest_eq)
    
    top_node = EquationHistory(eq1, 'start', None)
    search_list = [top_node]

    curr_history = top_node

    while True:
        # Apply every function to current eq
        for func in FUNC_LIST:
            variation_list = get_variations(func, curr_history.eq, max_depth)

            for var in variation_list:
                var_str = str(var)

                # If variation matches destination eq, or we are simplifying and the eq is as small as possible
                if var_str == dest_eq_str or (simplify and (isinstance(var, bool) or isinstance(var, SymbolEq))):
                    print('finished', len(search_list))
                    return EquationHistory(var, str(func), curr_history)

                # Else if the variation is not in the tested set
                elif not database.eq_exists(var_str):
                    database.add_eq(var_str)

                    new_hist = EquationHistory(var, str(func), curr_history)
                    search_list.append(new_hist)

                    # If trying to simplify and max_tests exceeded, abort
                    test_count = database.get_test_count()
                    if simplify and test_count > max_tests:
                        print('max tests')
                        return top_node

                    if test_count % 100000 == 0:
                        print(test_count)

        # Remove first node since all variations are catalogued
        # And attempt to select the next node, otherwise return
        del search_list[0]
        if len(search_list) > 0:
            curr_history = search_list[0]
        else:
            if simplify:
                print('list empty', len(tested_set))
                return top_node
            else:
                raise Exception("Proof failed.")

def parse_text(text):
    """
    Parse the string into a list of lists.

    Ex. "S and (P or R)" -> ['S', 'and' ['P', 'or' 'R']]

    :param text: Text to parse.
    :returns: List of items, with subitems as sublitsts.
    """
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
    """
    Parse equation list into an Equation object.
    Reuses equivalent symbols so all similar symbols are the same reference.

    :param parse_list: Parse list returned from parse_text.
    :param symbol_list: List of SymbolEq objects that have already been created.
    :returns: A single Equation obj, with appropriate Equations as arguments.
    """
    if len(parse_list) == 0:
        return parse_list[0]

    for i, x in enumerate(parse_list):
        if isinstance(x, list):
            parse_list[i] = parse_equation(x, symbol_list)

    if len(parse_list) == 0:
        return parse_list[0]

    # Convert all symbol and boolean tokens first.
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
    
    # Convert the rest in order of precedence.

    # While there is a token in the parse_list.
    while 'not' in parse_list:
        for i, x in enumerate(parse_list):
            if x == 'not':
                # Replace the token with the Equation obj, and the arguments consumed with None.
                parse_list[i] = NotEq(parse_list[i + 1])
                parse_list[i + 1] = None
                break
        
        # Filter the parse_list so to remove any consumed tokens.
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
    """ Return the 'start' equation from any given EquationHistory. """
    top_history = eq_history
    while eq_history.parent:
        top_history = top_history.parent
    
    return top_history

def get_lowest_depth(eq_history):
    """
    Find the child equation of a EquationHistory that is the smallest.

    :param eq_history: Parent EquationHistory.
    :returns: Equation history with the lowest depth Equation.
    """

    lowest_per_child = []
    for child in eq_history.children:
        lowest_per_child.append(get_lowest_depth(child))

    lowest = eq_history
    for child in lowest_per_child:
        if get_depth(child.eq) < get_depth(lowest.eq):
            lowest = child
    return lowest

def simplify(eq, max_depth=DEFAULT_MAX_DEPTH, max_tests=DEFAULT_MAX_TESTS):
    proof = prove(eq, None, simplify=True, max_depth=max_depth, max_tests=max_tests)
    return get_lowest_depth(proof)

def get_equation(text):
    return parse_equation(parse_text(text))