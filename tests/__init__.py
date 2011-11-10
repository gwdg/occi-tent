#!/usr/bin/env python3
'''
OCCI tent test modules.
'''

from inc.client import OCCIError

modules = {}
__all__ = []

def _importModules ( locals, globals ):
	'''Import submodules from the current package and expose them through the module.'''
	import os

	for file in os.listdir( os.path.dirname( __file__ ) ):
		if not file.endswith( '.py' ) or file.startswith( '__init__.' ):
			continue
		
		moduleName = file[:-3]
		if moduleName not in __all__:
			modules[moduleName] = __import__( moduleName, locals, globals )
			__all__.append( moduleName )

			for obj in modules[moduleName].__all__:
				modules['{0}.{1}'.format( moduleName, obj ) ] = getattr( modules[moduleName], obj )

def testModule ( function ):
	'''Decorate a callable as test module and expose it through the module.'''
	if '__all__' not in function.__globals__:
		function.__globals__['__all__'] = []
	function.__globals__['__all__'].append( function.__name__ )
		
	return function

# initialize module
_importModules( locals(), globals() )