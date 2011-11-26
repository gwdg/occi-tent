#!/usr/bin/env python3
'''
OCCI tent command line interface module.
'''

from inc.tent import Tent
from inc.yaml import YamlTest
from itertools import islice
from datetime import datetime
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
		t = YamlTest( '[module] ' + args.runmod )
		t.modules.append( { 'module' : args.runmod, 'chain' : None, 'parameters' : {} } )
		tent.runTests( ( t, ) )
		parser.exit()
	
	if not args.suite:
		parser.error( 'no test suite file given' )
	
	if args.list:
		printTestCases( args.suite.name, tent.loadTestCases( args.suite ) )
		parser.exit()
	
	if args.run:
		if args.run < 0:
			testCases = list( tent.loadTestCases( args.suite ) )
			printTestCases( args.suite.name, testCases )
			
			try:
				testNum = int( input( 'Execute which test? ' ) )
			except ValueError:
				testCase = None
			
			if testNum < 0 or testNum > len( testCases ):
				testCase = None
			else:
				testCase = testCases[testNum]
		else:
			testCase = next( islice( tent.loadTestCases( args.suite ), args.run, args.run + 1 ), None )
		
		if not testCase:
			parser.error( 'Invalid test case specification.' )
		
		print( 'Running single test.' )
		tent.runTests( ( testCase, ) )
		parser.exit()
	
	with open( '{}.log'.format( args.suite.name ), 'a+' ) as logFile:
		print( '=' * 50 + ' {0} =='.format( datetime.utcnow().isoformat( ' ' ) ), file=logFile )
		print( 'Running tests from `{0}`'.format( args.suite.name ) )
		tent.runSuite( args.suite, logFile )
		print( file=logFile )

def printTestCases ( suiteName, testCases ):
	print( 'Available test cases in `{0}`'.format( suiteName ) )
	for i, testCase in enumerate( testCases ):
		print( '[{: >2}] {}'.format( i, testCase.title ) )

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