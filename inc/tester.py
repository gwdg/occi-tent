#!/usr/bin/env python3
'''
OCCI tent tester.
'''

from .occi import *
from .client import *
from .util import safeRepr, timestamp

class SkipTestError ( Exception ):
	pass

class Tester:
	failureException = AssertionError

	def __init__ ( self, client ):
		self.client = client
		self.tests = []
		self.current = None
	
	def request ( self, *args, **kwargs ):
		return self.client.request( *args, **kwargs )
	
	def log ( self, *args, seperator=' ' ):
		if self.current is not None:
			self.current['log'].append( timestamp() + seperator.join( map( str, args ) ) )
	
	def run ( self, test, args = None, setUp = None, tearDown = None ):
		'''
		Run the given test. Optionally set up the text fixture before testing,
		and deconstruct it after testing if appropriate setUp and tearDown
		callables are specified.
		'''
		self.current = {
			'test' : test,
			'setUp' : setUp,
			'tearDown' : tearDown,
			'skipped' : False,
			'failed' : False,
			'log' : [] }

		if not isinstance( args, dict ):
			args = {}
		
		if setUp:
			setUp( self )
		
		try:
			test( self, **args )
		except SkipTestError as e:
			self.current['skipped'] = True
			self.log( '[SKIP] ' + e.args[0] )
		except self.failureException as e:
			self.current['failed'] = True
			self.log( '[FAIL] ' + e.args[0] )
		except Exception as e:
			self.current['failed'] = True
			self.log( '[ERROR] Unhandled exception {0}: {1}'.format( type( e ).__name__, ', '.join( map( str, e.args ) ) ) )
		
		if tearDown:
			tearDown( self )
		
		self.tests.append( self.current )
	
	def _failException ( self, message, defaultMessage = '', *args ):
		'''
		Create a failure exception with the given message or fall back to the
		default message and use the additional arguments to format it.
		'''
		if message is None:
			message = defaultMessage.format( *args )
		return self.failureException( message )

	def fail ( self, msg = None ):
		'''Fail immediately.'''
		raise self._failException( msg )
	
	def skip ( self, msg = None ):
		'''Skip current test.'''
		raise SkipTestError( msg )
	
	# Assertions
	def assertFalse ( self, expr, msg = None ):
		'''Fail if expression does is not false.'''
		if expr:
			raise self._failException( msg, '{0} is not false', safeRepr( expr ) )
	
	def assertTrue ( self, expr, msg = None ):
		'''Fail if expression does is not true.'''
		if not expr:
			raise self._failException( msg, '{0} is not true', safeRepr( expr ) )
	
	def assertEqual ( self, expr, other, msg = None ):
		'''Fail if expression does not equal (==) the other expression.'''
		if not expr == other:
			raise self._failException( msg, '{0} != {1}', safeRepr( expr ), safeRepr( other ) )
	
	def assertNotEqual ( self, expr, other, msg = None ):
		'''Fail if expression does equal (==) the other expression.'''
		if expr == other:
			raise self._failException( msg, '{0} == {1}', safeRepr( expr ), safeRepr( other ) )
	
	def assertIn ( self, expr, seq, msg = None ):
		'''Fail if expression is not in the sequence.'''
		if expr not in seq:
			raise self._failException( msg, '{0} is not in {1}', safeRepr( expr ), safeRepr( seq ) )
	
	def assertNotIn ( self, expr, seq, msg = None ):
		'''Fail if expression is in the sequence.'''
		if expr in seq:
			raise self._failException( msg, '{0} is in {1}', safeRepr( expr ), safeRepr( seq ) )