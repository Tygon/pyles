import unittest

from pyles.identities import *
from pyles.solve import get_equation

class TestLogic(unittest.TestCase):
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