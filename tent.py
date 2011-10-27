#!/usr/bin/env python3
'''
OCCI tent command line interface module.
'''

from inc.tent import Tent
import argparse, sys

parser = argparse.ArgumentParser( description='OCCI tent command line interface', epilog=None )
parser.add_argument( '--version', action='version', version='OCCI tent v1.0' )
parser.add_argument( '--config', default='config.yaml', type=open, help='configuration file (default: %(default)s)', metavar='FILE' )
parser.add_argument( '--modules', action='store_true', help='list all available test modules' )
parser.add_argument( '-l', '--list', action='store_true', help='list all available tests' )
parser.add_argument( '--show', help='show test or test module information', metavar='TEST' )
parser.add_argument( 'tests', nargs='*', help='tests or test suites to run' )

def main ():
	args = parser.parse_args()
	tent = Tent( args.config )

	if args.modules:
		printModuleList( tent )
		parser.exit()
	
	if len( args.tests ) > 0:
		raise NotImplementedError( 'Not yet available. Call without arguments.' )
	else:
		print( 'Running tests from `tests.yaml` file' )
		tent.runTestsFromFile( 'tests.yaml' )


def printModuleList ( tent ):
	for module in tent.modules:
		if module['doc']:
			print( '{name} : {doc}'.format( **module ) )
		else:
			print( module['name'] )
		
		for function in module['functions']:
			if function['doc']:
				print( '- {name} : {doc}'.format( **function ) )
			else:
				print( '- {name}'.format( **function ) )
			
			for param in function['params']:
				print( '  - {name} : {annotation}'.format( **param ) )
				if param['default']:
					print( '    default value: ' + repr( param['default'] ) )

if __name__ == '__main__':
	main()