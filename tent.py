#!/usr/bin/env python3
'''
OCCI tent command line interface module.
'''

from inc.tent import Tent
import argparse, sys

parser = argparse.ArgumentParser( description='OCCI tent command line interface', epilog=None )
parser.add_argument( '--version', action='version', version='OCCI tent v1.0' )
parser.add_argument( '--config', '-c', default='config.yaml', type=open, help='configuration file (default: %(default)s)', metavar='FILE' )
parser.add_argument( '--modules', action='store_true', help='list all available test modules' )

parser.add_argument( '--list', '-l', action='store_true', help='list available test cases from test suite' )
parser.add_argument( '--run', '-r', nargs='?', const=-1, type=int, help='run single test case from test suite', metavar='ID' )
parser.add_argument( '--runmod', help='run single, parameterless test module', metavar='MODULE' )
parser.add_argument( 'suite', nargs='?', type=open, help='test suite file to use' )

def main ():
	try:
		args = parser.parse_args()
	except IOError as e:
		parser.error( str( e ) )
	tent = Tent( args.config )
	
	if args.modules:
		printModuleList( tent )
		parser.exit()
	
	if args.runmod:
		try:
			tent.runTest( args.runmod, None )
		except ValueError:
			parser.error( 'test module not found: ' + test )
		parser.exit()
	
	if not args.suite:
		parser.error( 'no test suite file given' )
	
	if args.list:
		parser.error( 'Sorry, not yet implemeted.' )
	
	if args.run:
		parser.error( 'Sorry, not yet implemeted.' )

	print( 'Running tests from `{0}`'.format( args.suite.name ) )
	tent.runTestsFromFile( args.suite )

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