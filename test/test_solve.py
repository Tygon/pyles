import unittest

from pyles.solve import *
from pyles.equation import *
from pyles.identities import *

class TestLogic(unittest.TestCase):
    def test_get_equation(self):
        eq = get_equation('True')
        self.assertEqual(eq, True)

        eq = get_equation('P and True')
        manual_eq = AndEq(SymbolEq('P'), True)
        self.assertEqual(eq, manual_eq)

        eq = get_equation("not (not P)")
        manual_eq = NotEq(NotEq(SymbolEq("P")))
        self.assertEqual(eq, manual_eq)

        eq = get_equation("P and P and P")
        manual_eq = AndEq(AndEq(SymbolEq("P"), SymbolEq("P")), SymbolEq("P"))
        self.assertEqual(eq, manual_eq)

    def test_get_variations(self):
        eq = get_equation("((P and Q) and R) and S")

        variation_list = get_variations(commutative, eq)

        self.assertEqual(len(variation_list), 3)

        self.assertIn(get_equation("S and ((P and Q) and R)"), variation_list)
        self.assertIn(get_equation("(R and (P and Q)) and S"), variation_list)
        self.assertIn(get_equation("((Q and P) and R) and S"), variation_list)

    def test_hash(self):
        eq1 = get_equation("not P and Q or R -> S")
        eq2 = get_equation("not P and Q or R -> S")
        self.assertEqual(hash(eq1), hash(eq2))

        eq2 = get_equation("not P and Q or R -> T")
        self.assertNotEqual(hash(eq1), hash(eq2))

        eq1 = get_equation("(((c or ((not a) or a)) and (a or (a -> b))) or (b -> c))")
        eq2 = get_equation("((((c or (not a)) or a) and (a or (a -> b))) or (b -> c))")
        self.assertNotEqual(hash(eq1), hash(eq2))

        eq1 = get_equation("((a or c) or ((not b) or ((c or (not a)) and (b or (not a)))))")
        eq2 = get_equation("(c or ((a or (not b)) or ((c or (not a)) and (b or (not a)))))")
        self.assertNotEqual(hash(eq1), hash(eq2))

        eq1 = get_equation("(((a or (b -> c)) or (b or (not a))) and ((c or (not a)) or (a or ((not b) or c))))")
        eq2 = get_equation("(((a or (b -> c)) or (c or (not a))) and ((b or (not a)) or (a or ((not b) or c))))")
        self.assertNotEqual(hash(eq1), hash(eq2))

        eq1 = get_equation("((b -> c) or (a or (((c or (not a)) and b) or ((c or (not a)) and (not a)))))")
        eq2 = get_equation("(a or ((b -> c) or (((c or (not a)) and b) or ((c or (not a)) and (not a)))))")
        self.assertNotEqual(hash(eq1), hash(eq2))

        variation_list = get_variations(commutative, eq1)
        self.assertNotIn(hash(eq1), variation_list)

    def test_prove(self):
        # self.skipTest('r')
        eq = get_equation("(a or (b -> c)) or ((c or not a) and (b or not a))")

        try:
            new_eq = prove(eq, True, max_depth=get_depth(eq) + 1)
        except Exception:
            self.fail()

    def test_simplify(self):
        # self.skipTest('r')
        eq = get_equation("(a or (b -> c)) or ((c or not a) and (b or not a))")
        history = simplify(eq, max_depth=get_depth(eq) + 1)
        self.assertEqual(history.eq, True)

if __name__ == '__main__':
    unittest.main()