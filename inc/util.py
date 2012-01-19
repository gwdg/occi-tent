#!/usr/bin/env python3
'''
OCCI tent utilties.
'''

import time
import urllib.parse, urllib.request

class Request ( urllib.request.Request ):
	'''urllib.request.Request extension supporting other HTTP methods.'''
	def __init__ ( self, url, data = None, headers = {}, origin_req_host = None, unverifiable = False, method = None ):
		self.method = method
		urllib.request.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
	
	def get_method ( self ):
		if self.method is not None:
			return self.method
		elif self.data is not None:
			return 'POST'
		else:
			return 'GET'


def quote ( text, safe = '~' ):
	'''Quote variable text. Defaults to RFC3986 behaviour.'''
	if isinstance( text, bytes ):
		return urllib.parse.quote_from_bytes( text, safe )
	return urllib.parse.quote( str( text ), safe )

def urlencodeData ( data = None ):
	'''URL encode data, matching the `application/x-www-form-urlencoded` MIME type.'''
	try:
		return '&'.join( quote( k ) + '=' + quote( v ) for k, v in query.items() )
	except AttributeError:
		return data

def safeRepr ( obj ):
	'''Generate a safe string representation of the given object.'''
	try:
		return repr( obj )
	except Exception:
		return object.__repr__( obj )

def timestamp ():
	'''Generate a timestamp string of the current time.'''
	t = time.time()
	return '{:02g}:{:02g}:{:07.4f}: '.format( t // 3600 % 24, t // 60 % 60, t % 60 )

def clonedPrinter ( secondChannel ):
	'''Clone the printer to a second channel if it exists.'''
	if not secondChannel:
		return print
	
	def prnt ( *args, **kwargs ):
		print( *args, **kwargs )
		print( *args, file=secondChannel, **kwargs )
	return prnt

def suiteOpener ( *args, **kwargs ):
	try:
		return open( *args, **kwargs )
	except IOError as e:
		if e.errno == 2:
			path = 'suites/' + e.filename
			if not path.endswith( '.yaml' ):
				path += '.yaml'
			return open( path, **kwargs )
		raise