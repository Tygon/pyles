import unittest

from logixell.main import *

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

    def test_identity(self):
        self.func_helper(identity, "P and True", "P")
        self.func_helper(identity,"Q or False", "Q")

    def test_idempotent(self):
        self.func_helper(idempotent,"P and P", "P")
        self.func_helper(idempotent,"Q or Q", "Q")

    def test_domination(self):
        self.func_helper(domination,"P or True", "True")
        self.func_helper(domination,"Q and False", "False")

    def test_commutative(self):
        self.func_helper(commutative,"P and Q", "Q and P")
        self.func_helper(commutative,"P or Q", "Q or P")

    def test_associative(self):
        self.func_helper(associative,"(P and Q) and R", "P and (Q and R)")
        self.func_helper(associative,"(P or Q) or R", "P or (Q or R)")

    def test_distributive(self):
        self.func_helper(distributive,"P or (Q and R)", "(P or Q) and (P or R)")
        self.func_helper(distributive,"P and (Q or R)", "(P and Q) or (P and R)")

    def test_negation(self):
        self.func_helper(negation,"P and not P", "False")
        self.func_helper(negation,"P or not P", "True")

    def test_absorption(self):
        self.func_helper(absorption,"P and (P or Q)", "P")
        self.func_helper(absorption,"P or (P and Q)", "P")
    
    def test_double_negation(self):
        self.func_helper(double_negation,"not (not P)", "P")

    def test_implication_equivalence(self):
        self.func_helper(implication_equivalence,"P -> Q", "not P or Q")
        self.func_helper(implication_equivalence,"not P or Q", "P -> Q")

    def test_biconditional_equivalence(self):
        self.func_helper(biconditional_equivalence,"P <-> Q", "(P -> Q) and (Q -> P)")
        self.func_helper(biconditional_equivalence,"(P -> Q) and (Q -> P)", "P <-> Q")

    def test_demorgans_law(self):
        self.func_helper(demorgans_law,"not (P and Q)", "not P or not Q")
        self.func_helper(demorgans_law,"not P or not Q", "not (P and Q)")

        self.func_helper(demorgans_law,"not (P or Q)", "not P and not Q")
        self.func_helper(demorgans_law,"not P and not Q", "not (P or Q)")

    def func_helper(self, func, txt_before, txt_after):
        eq_before = get_equation(txt_before)
        eq_after = func(eq_before)

        self.assertEqual(eq_before, get_equation(txt_before))
        self.assertEqual(eq_after, get_equation(txt_after))

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
            new_eq = prove(eq, True)
        except Exception:
            self.fail()

    def test_simplify(self):
        self.skipTest('r')
        eq = get_equation("(a or (b -> c)) or ((c or not a) and (b or not a))")
        history = simplify(eq)
        self.assertEqual(history.eq, True)

    


if __name__ == '__main__':
    unittest.main()