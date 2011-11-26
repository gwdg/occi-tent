#!/usr/bin/env python3
'''
YAML utility functions and class representations.
'''

import yaml
from yaml import YAMLError, YAMLObject
try:
	from yaml import CSafeLoader as YAMLLoader, CSafeDumper as YAMLDumper
except ImportError:
	from yaml import SafeLoader as YAMLLoader, SafeDumper as YAMLDumper

#__all__ = [ 'YAMLError', 'yamlLoad', 'yamlDump', 'YamlTest', 'YamlSuite' ]

# Wrapper
def yamlLoad ( stream, first = False ):
	'''
	Safely parse all YAML documents in the given stream and return a generator
	of corresponding Python objects for each document.
	Alternatively parse only the first document if `first` is true.
	'''
	if first:
		return yaml.load( stream, Loader = YAMLLoader )
	else:
		return yaml.load_all( stream, Loader = YAMLLoader )

def yamlDump ( data, stream = None, **kwargs ):
	'''
	Safely serialize a single, or a sequence of Python objects into a YAML
	document stream. Return the produced YAML string unless `stream` is set.
	Accept a number of keyword arguments also available to the original
	`yaml.dump` function.
	'''
	if not isinstance( data, tuple ) and not isinstance( data, list ):
		data = ( data, )
	
	return yaml.dump( data, Dumper = YAMLDumper, stream = stream, **kwargs )

# YAML class representations
class YamlTest ( YAMLObject ):
	'''YAML object representation for a defined test.'''
	yaml_tag = '!Test'
	yaml_loader = YAMLLoader
	yaml_dumper = YAMLDumper

	def __init__ ( self, title = '' ):
		self.title = title
		self.modules = []
	
	def __setstate__ ( self, state ):
		self.__dict__.update( state )