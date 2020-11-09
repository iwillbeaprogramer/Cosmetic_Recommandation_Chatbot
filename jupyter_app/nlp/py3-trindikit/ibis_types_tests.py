# -*- encoding: utf-8 -*-

#
# ibis_types_tests.py
# Copyright (C) 2010, Alexander Berman. All rights reserved.
#
# This file contains unit tests for IBIS types.
#

from ibis import *
import unittest

class IbisTypesTests(unittest.TestCase):
    def test_Atomic(self):
        # integer
        x = Ind(123)
        self.assertEqual(x.content, 123)
        self.assertNotEqual(x.content, "123")

        # string
        x = Ind("paris")
        self.assertEqual(x.content, "paris")
        self.assertRaises(AssertionError, Ind, "1paris")
        self.assertRaises(AssertionError, Ind, "p!aris")
        self.assertRaises(AssertionError, Ind, "paris()")
        x = Ind("paris_france")
        self.assertRaises(AssertionError, Ind, "_paris")

    def test_Ans(self):
        # proposition
        ans = Ans("city(paris)")
        self.assertEqual(type(ans), Prop)
        self.assertEqual(ans.pred, Pred1("city"))
        self.assertEqual(ans.ind.content, "paris")

        # short answer
        ans = Ans("paris")
        self.assertEqual(type(ans), ShortAns)
        self.assertEqual(ans.ind.content, "paris")

        # Y/N answer
        ans = Ans("yes")
        self.assertEqual(type(ans), YesNo)
        self.assertEqual(ans.yes, True)

        ans = Ans("no")
        self.assertEqual(type(ans), YesNo)
        self.assertEqual(ans.yes, False)

    def test_Answer(self):
        # proposition
        ans = Answer("city(paris)")
        prop = ans.content
        self.assertEqual(type(prop), Prop)
        self.assertEqual(prop.pred, Pred1("city"))
        self.assertEqual(prop.ind.content, "paris")

        # short answer
        ans = Answer("paris")
        self.assertEqual(type(ans.content), ShortAns)
        self.assertEqual(ans.content.ind.content, "paris")

        # Y/N answer
        ans = Answer("yes")
        self.assertEqual(type(ans.content), YesNo)
        self.assertEqual(ans.content.yes, True)

        ans = Answer("no")
        self.assertEqual(type(ans.content), YesNo)
        self.assertEqual(ans.content.yes, False)

    def test_Prop(self):
        p = Prop("return()")
        self.assertEqual(str(p), "return()")
        self.assertEqual(p.pred, Pred0("return"))
        self.assertEqual(p.yes, True)

        p = Prop("-return()")
        self.assertEqual(str(p), "-return()")
        self.assertEqual(p.pred, Pred0("return"))
        self.assertEqual(p.yes, False)

        p = Prop("dest_city(paris)")
        self.assertEqual(str(p), "dest_city(paris)")
        self.assertEqual(p.pred, Pred1("dest_city"))
        self.assertEqual(p.ind, Ind("paris"))
        self.assertEqual(p.yes, True)

        p = Prop("-dest_city(paris)")
        self.assertEqual(str(p), "-dest_city(paris)")
        self.assertEqual(p.pred, Pred1("dest_city"))
        self.assertEqual(p.ind, Ind("paris"))
        self.assertEqual(p.yes, False)

    def test_Question(self):
        # Y/N questions
        q = Question("?return()")
        self.assertEqual(str(q), "?return()")
        self.assertEqual(type(q), YNQ)
        self.assertEqual(q.prop.pred, Pred0("return"))
        self.assertEqual(q.prop.yes, True)

        q = Question("?-return()")
        self.assertEqual(str(q), "?-return()")
        self.assertEqual(type(q), YNQ)
        self.assertEqual(q.prop.pred, Pred0("return"))
        self.assertEqual(q.prop.yes, False)

        q = Question("?dest_city(paris)")
        self.assertEqual(str(q), "?dest_city(paris)")
        self.assertEqual(type(q), YNQ)
        self.assertEqual(q.prop.pred, Pred1("dest_city"))
        self.assertEqual(q.prop.ind, Ind("paris"))
        self.assertEqual(q.prop.yes, True)

        q = Question("?-dest_city(paris)")
        self.assertEqual(str(q), "?-dest_city(paris)")
        self.assertEqual(type(q), YNQ)
        self.assertEqual(q.prop.pred, Pred1("dest_city"))
        self.assertEqual(q.prop.ind, Ind("paris"))
        self.assertEqual(q.prop.yes, False)

        # WHQ questions
        q = Question("?x.dest_city(x)")
        self.assertEqual(str(q), "?x.dest_city(x)")
        self.assertEqual(type(q), WhQ)
        self.assertEqual(q.pred, Pred1("dest_city"))

        # Alt questions
        q = AltQ(YNQ("city(paris)"), YNQ("city(london)"))
        self.assertEqual(type(q), AltQ)
        self.assertEqual(len(q.ynqs), 2)
        self.assertEqual(q.ynqs[0], YNQ("city(paris)"))
        self.assertEqual(q.ynqs[1], YNQ("city(london)"))

    def test_PlanConstructor(self):
        x = Respond("?return()")
        self.assertEqual(str(x), "Respond('?return()')")
        self.assertEqual(type(x.content), YNQ)
        
        x = ConsultDB("?return()")
        self.assertEqual(str(x), "ConsultDB('?return()')")
        self.assertEqual(type(x.content), YNQ)
        
        x = Findout("?return()")
        self.assertEqual(str(x), "Findout('?return()')")
        self.assertEqual(type(x.content), YNQ)
        
        x = Raise("?return()")
        self.assertEqual(str(x), "Raise('?return()')")
        self.assertEqual(type(x.content), YNQ)

        x = If("?return()", [Findout("?x.return_day(x)")])
        self.assertEqual(x.cond, YNQ("return()"))
        self.assertEqual(x.iftrue, tuple([Findout("?x.return_day(x)")]))
        self.assertEqual(x.iffalse, ())

if __name__ == '__main__':
    unittest.main()
