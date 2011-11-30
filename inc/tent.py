#!/usr/bin/env python3
'''
OCCI tent core.
'''

import inspect

from .client import OCCIClient
from .tester import Tester
from .util import clonedPrinter
from .yaml import *
import tests

class Tent:
	_modules = None
	
	def __init__ ( self, configurationFile ):
		if isinstance( configurationFile, str ):
			configurationFile = open( configurationFile )
		self.rawConfig = yamlLoad( configurationFile, first=True )
		configurationFile.close()
		
		self.serverHost = self.rawConfig['host']
		self.serverPort = self.rawConfig['port']
		
		self.client = OCCIClient( self.serverHost, self.serverPort )
	
	def runTest ( self, module, args ):
		if module not in tests.modules:
			raise ValueError( 'Unknown test method' )
		
		tester = Tester( self.client )
		tester.run( tests.modules[module], args=args )
		t = tester.current
		
		print( 'Test: ' + t['test'].__name__ )
		print( '\n'.join( t['log'] ) )
		
		if t['skipped']:
			print( 'Test skipped.' )
		if t['failed']:
			print( 'Test failed.' )
		else:
			print( 'Test successful.' )
	
	def runSuite ( self, suiteFile, logFile = None ):
		'''Run test suite.'''
		testCases = self.loadTestCases( suiteFile )
		return self.runTests( testCases, logFile )
	
	def runTests ( self, testCases, logFile = None ):
		'''Run test cases.'''
		tester = Tester( self.client )
		total, failed, skipped = 0, 0, 0
		print = clonedPrinter( logFile )
		
		for case in testCases:
			print( 'Test: ' + case.title )
			tester.start( case.title )
			
			for module in case.modules:
				parameters = module['parameters']
				if module['chain'] and module['chain'] not in parameters:
					parameters[module['chain']] = tester.current['result']
				
				tester.run( tests.modules[module['module']], args=parameters )
				
				if tester.current['skipped'] or tester.current['failed']:
					break
			
			t = tester.current
			if t['log']:
				print( '    ' + '\n    '.join( t['log'] ) )
			
			total += 1
			if t['skipped']:
				skipped += 1
			if t['failed']:
				failed += 1
		
		print()
		print( 'Ran {0} tests: {1} successful, {2} failed, {3} skipped.'.format( total, total - failed - skipped, failed, skipped ) )
	
	def loadTestCases ( self, suiteFile ):
		'''Load test cases from suite file.'''
		if isinstance( suiteFile, str ):
			suiteFile = open( suiteFile )
		
		for testCase in yamlLoad( suiteFile ):
			if not isinstance( testCase, YamlTest ):
				t = YamlTest()
				t.__setstate__( testCase )
				testCase = t
			
			for module in testCase.modules:
				module.setdefault( 'module' )
				module.setdefault( 'chain' )
				module.setdefault( 'parameters', {} )
			
			yield testCase
		
		suiteFile.close()
	
	@property
	def modules ( self ):
		'''Test module index.'''
		if not self._modules:
			self._modules = []
			for moduleName in tests.__all__:
				module = getattr( tests, moduleName )
				
				functions = []
				for funcName in module.__all__:
					func = getattr( module, funcName )
					spec = inspect.getfullargspec( func )
					args = zip( spec.args, ( len( spec.args ) - len( spec.defaults or () ) ) * ( NotImplemented, ) + ( spec.defaults or () ) )
					next( args )
					
					params = []
					for ( arg, default ) in args:
						params.append( {
							'name' : arg,
							'default' : None if default is NotImplemented else 'None' if default is None else default,
							'annotation' : spec.annotations.get( arg )
							} )
					
					if spec.varargs:
						params.append( {
							'name' : '*' + spec.varargs,
							'default' : None,
							'annotation' : spec.annotations.get( spec.varargs )
						} )
					
					if spec.varkw:
						params.append( {
							'name' : '**' + spec.varkw,
							'default' : None,
							'annotation' : spec.annotations.get( spec.varkw )
						} )
					
					functions.append( {
						'name' : funcName,
						'function' : func,
						'doc' : inspect.getdoc( func ),
						'params' : params
					} )
				
				self._modules.append( {
					'name' : moduleName,
					'module' : module,
					'doc' : inspect.getdoc( module ),
					'functions' : functions
				} )
		
		return self._modules
		
		@modules.deleter
		def modules ( self ):
			self._modules = None