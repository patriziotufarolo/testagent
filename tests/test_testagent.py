#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
"""
test_testagent
----------------------------------

Tests for `testagent` module.
"""

import unittest

from testagent.tasks import start_certification

class TestTestagent(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        assert (start_certification.delay('''
        <collector id="1" cmid="1" probe_driver="EmptyProbeDelay">
                <TestCases>
                    <TestCase>
                        <ID>1</ID>
                        <Description>TestCase1</Description>
                        <TestInstance Operation="1">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input1" value="Value1" />
                                <Item key="Input2" value="Value2" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                        <TestInstance Operation="3">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input6" value="Value6" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                        <TestInstance Operation="2">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input8" value="Value8" />
                                <Item key="Input5" value="Value9" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                    </TestCase>
                </TestCases>
                </collector>
        '''))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
