#!/usr/bin/env python3
'''
OCCI client.
'''

from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from .occi import *
from .util import Request, urlencodeData

class OCCIResponse:
	'''OCCI response wrapper.'''

	def __init__ ( self, response ):
		self.rsp  = response
		self.info = response.info()
		self.body = response.read().decode()
		self.status = response.code

		contentType = self.rsp.getheader( 'Content-Type' )
		if contentType == 'text/uri-list':
			self.uris = self.body.split( '\n\r' )
		elif contentType == 'text/occi':
			pass
		else: # contentType == 'text/plain':
			self.structures = [ self.parseStructure( line.strip() ) for line in self.body.strip().split( '\n' ) ]
	
	def close ( self ):
		'''Close the response.'''
		self.rsp.close()
	
	@staticmethod
	def parseStructure ( line, strict = False ):
		'''Parse the structure in the given line.'''
		if line.startswith( 'Category:' ):
			return CategoryStructure.parse( line, strict=strict )
		elif line.startswith( 'Link:' ):
			return LinkStructure.parse( line, strict=strict )
		elif line.startswith( 'X-OCCI-Location' ):
			return LocationStructure.parse( line, strict=strict )
		elif line.startswith( 'X-OCCI-Attribute:' ):
			return AttributeStructure.parse( line, strict=strict )
		elif strict and line != '':
			raise TypeError( 'Invalid response data' )
		else:
			return line

class OCCIError ( Exception ):
	'''OCCI error.'''

	def __init__ ( self, response ):
		self.rsp = response
		self.info = response.info()
		self.body = response.read().decode()
		self.status = response.code
		super().__init__( self, response )


class OCCIClient:
	userAgent = 'occi-tent/1.0 python/3.2 OCCI/1.1'

	def __init__ ( self, host, port ):
		self.host = host
		self.port = port
		self.baseUrl = 'http://' + str( host ) + ':' + str( port )
	
	def makeUrl ( self, path ):
		if not path.startswith( '/' ):
			path = '/' + path
		return self.baseUrl + path
	
	def request ( self, method, path, accept = None, data = None, headerData = None ):
		method = method.upper()
		url = self.makeUrl( path )
		req = Request( url )
		req.method = method if method in ( 'GET', 'POST', 'PUT', 'DELETE' ) else 'GET'
		req.add_header( 'User-agent', self.userAgent )

		if accept:
			req.add_header( 'Accept', accept )
		else:
			req.add_header( 'Accept', 'text/occi, text/plain' )
		
		if headerData:
			if isinstance( headerData, dict ):
				for key, value in headerData.items():
					req.add_header( key, value )
			else:
				hasStructures = False
				for value in headerData:
					if isinstance( value, OCCIStructure ):
						# TODO: Revise composite header fields.
						if value.headerName in req.headers:
							req.headers[value.headerName] += ', ' + repr( value )
						else:
							req.headers[value.headerName] = repr( value )
						hasStructures = True
					elif isinstance( value, dict ):
						for key, value in value.items():
							req.add_header( key, value )
					else:
						raise TypeError( 'Invalid header data.' )
				
				if hasStructures and not req.has_header( 'Content-type' ):
					req.add_unredirected_header( 'Content-type', 'text/occi' )
		
		if data:
			if isinstance( data, bytes ):
				req.data = data
			elif isinstance( data, str ):
				req.data = data.encode()
			elif isinstance( data, dict ):
				req.data = urlencodeData( data )
				
				if not req.has_header( 'Content-type' ):
					req.add_unredirected_header( 'Content-type', 'application/x-www-form-urlencoded' )
			else:
				# assume general sequence
				req.data = b'\n\r'.join( map( lambda x: x if isinstance( x, bytes ) else str( x ).encode(), data ) )

				# set content type if not set by now
				if not req.has_header( 'Content-type' ):
					# TODO: Check spec on this.
					req.add_unredirected_header( 'Content-type', 'text/plain' )
		
		# perform request
		try:
			return OCCIResponse( urlopen( req ) )
		except HTTPError as e:
			raise OCCIError( e )
	

	## deprecated
	def open ( self, path, method = 'GET', data = None, accept = None, inHead = False ):
		if inHead:
			return self.request( method, path, accept = accept, headerData = data )
		else:
			return self.request( method, path, accept = accept, data = data )