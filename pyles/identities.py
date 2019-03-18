from .equation import AndEq, OrEq, NotEq, ImpliesEq, BiImpliesEq

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
    else:
        return NotEq(NotEq(eq))

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


FUNC_LIST = [identity, idempotent, domination, commutative, associative, distributive, negation, absorption, double_negation, demorgans_law, implication_equivalence, biconditional_equivalence]