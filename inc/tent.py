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
		with open( configurationFile ) as f:
			self.rawConfig = yamlLoad( f, first=True )
		self.serverHost = self.rawConfig['host']
		self.serverPort = self.rawConfig['port']

		self.client = OCCIClient( self.serverHost, self.serverPort )
	
	def runTestsFromFile ( self, fileName ):
		tester = Tester( self.client )

		with open( fileName ) as f:
			for test in yamlLoad( f ):
				if not isinstance( test, YamlTest ):
					t = YamlTest()
					t.__setstate__( test )
					test = t
				
				print( 'Executing test: ' + test.name )
				for module in test.modules:
					tester.run( tests.modules[module['module']], args=module['parameters'] )
	
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
					args = zip( spec.args, ( len( spec.args ) - len( spec.defaults or () ) ) * ( None, ) + ( spec.defaults or () ) )
					next( args )
					
					params = []
					for ( arg, default ) in args:
						params.append( {
							'name' : arg,
							'default' : default,
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
						'doc' : func.__doc__,
						'params' : params
					} )
				
				self._modules.append( {
					'name' : moduleName,
					'module' : module,
					'doc' : module.__doc__,
					'functions' : functions
				} )
		
		return self._modules

		@modules.deleter
		def modules ( self ):
			self._modules = None