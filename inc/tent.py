#!/usr/bin/env python3
'''
OCCI tent core.
'''
import inspect

from .tester import Tester
from .client import OCCIClient
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
		
	def runTestsFromFile ( self, fileName ):
		tester = Tester( self.client )
		failed, skipped = 0, 0
		
		with open( fileName ) as f:
			for test in yamlLoad( f ):
				if not isinstance( test, YamlTest ):
					t = YamlTest()
					t.__setstate__( test )
					test = t
				
				for module in test.modules:
					tester.run( tests.modules[module['module']], args=module['parameters'] )
					
					t = tester.current
					print( 'Test: ' + t['test'].__name__ )
					print( '\n'.join( t['log'] ) )
					print( '---' )
					
					if t['skipped']:
						skipped += 1
					if t['failed']:
						failed += 1
		
		print( 'Ran {0} tests: {1} successful, {2} failed, {3} skipped.'.format( len( tester.tests ), len( tester.tests ) - failed - skipped, failed, skipped ) )
	
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