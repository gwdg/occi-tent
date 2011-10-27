#!/usr/bin/env python3
'''
OCCI tent command line interface module.
'''

from inc.tent import Tent
import getopt, sys

configurationFile = 'config.yaml'

def main ( argv ):
	print( 'OCCI tent command line interface' )

	try:
		opts, args = getopt.getopt( argv, 'hl', ( 'help', 'list', 'modules', 'show' ) )
	except getopt.GetoptError as e:
		print( e )
		printUsage()
		sys.exit( 2 )
	
	tent = Tent( configurationFile )

	for o, a in opts:
		if o in ( '-h', '--help' ):
			printHelp()
			sys.exit()
		elif o in ( '-l, --list' ):
			pass
		elif o == '--modules':
			printModuleList( tent )
			sys.exit()
		elif o == '--show':
			pass
		else:
			assert False, 'unhandled command argument'
	
	# run tests
	if len( args ) != 0:
		print( 'Running tests', ';'.join(args) )
		raise NotImplemented()
	else:
		print( 'Running tests from `tests.yaml` file' )
		tent.runTestsFromFile( 'tests.yaml' )

def printHelp ():
	print( 'tent [<options>] <tests>')
	print()
	print( 'Options and command line arguments:' )
	print( ' -h, --help       Show this help' )
	print( ' -l, --list       List all available tests' )
	print( ' --modules        List all available test modules' )
	print( ' --show <test>    Show test information' )
	print( ' --show <module>  Show test module information')
	print( ' tests            Tests or test suites to run')

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
	main( sys.argv[1:] )