#!/usr/bin/env python3
'''
Simple example test modules.
'''

from . import testModule

@testModule
def simple ( t ):
	t.log( 'This is inside the test!' )
	t.assertTrue( True )
	t.assertFalse( False )
	t.assertEqual( 2, 2.0 )

@testModule
def parameterized ( t, param1 : 'first parameter', param2 : 'second parameter' = 'default value for second parameter' ):
	t.log( param1 )
	t.log( param2 )
	t.assertTrue( True )

@testModule
def returningTest ( t ):
	return 'a return value'

@testModule
def failingTest ( t ):
	t.fail( 'I fail.' )

@testModule
def skippingTest ( t ):
	t.skip( 'I skip.' )

@testModule
def incrementing ( t, number : 'number to increment' = 0 ):
	t.log( 'current number:', number )
	return number + 1