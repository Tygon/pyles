import abc

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