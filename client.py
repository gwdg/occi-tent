from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from inc.occi import *
from inc.yaml import *
from inc.client import *

#OCCIClient.userAgent = 'occi-tent/1.0 python/3.2 OCCI/1.1'

with open( 'config.yaml' ) as f:
	config = yamlLoad( f, first=True )
client = OCCIClient( config['host'], config['port'] )

if False:
	cats = {}
	try:
		r = client.open( '/-/', 'GET' )
		#print( r.info )
		#print( r.body )
		for structure in r.structures:
			cats[ structure.term ] = structure
		r.close()
	except OCCIError as e:
		print( e.info )
		print( e.body )
		e.close()
	else:
		print( cats['compute'] )

		cat = CategoryStructure()
		cat.term = 'compute'
		cat.attrs['scheme'] = unquote( cats['compute'].attrs['scheme'] )
		cat.attrs['class'] = 'kind'

		try:
			r = client.open( '/compute/', 'POST', data = ( cat, ), accept = 'text/occi' )
			print( r.info )
			print( r.body )
			r.close()
		except OCCIError as e:
			print( 'err' )
			print( e.info )
			print( e.body )
			e.rsp.close()
elif True:
	try:
		r = client.open( '/-/', 'GET' ) # , accept='text/occi'
		print( r.info )
		print( r.body )

		for s in r.structures:
			print( s )

		r.close()
	except OCCIError as e:
		print( 'err' )
		print( e.info )
		print( e.body )
		e.rsp.close()
else:
	cat = CategoryStructure()
	cat.term = 'compute'
	cat.attrs['scheme'] = 'http://schemas.ogf.org/occi/infrastructure#'
	cat.attrs['class'] = 'kind'

	try:
		r = client.open( '/compute/', 'POST', data = ( cat, ), accept = 'text/occi' )
		print( r.info )
		print( r.body )
		r.close()
	except OCCIError as e:
		print( 'err' )
		print( e.info )
		print( e.body )
		e.close()