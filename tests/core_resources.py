#!/usr/bin/env python3
'''
OCCI core tests: Resource-related operations.
'''

import random

from . import testModule, OCCIError
from inc.occi import *

@testModule
def createResource ( t ) -> 'URI of created resource instance':
	'''Create a (predefined) resource instance.'''
	storageKind = KindStructure( 'storage', 'http://schemas.ogf.org/occi/infrastructure#' )
	attributes = AttributeStructure()
	attributes['occi.storage.size'] = '10'
	
	rsp = t.request( 'POST', '/storage/', headerData=( storageKind, attributes ) )
	t.assertEqual( rsp.status, 200 )
	t.assertTrue( len( rsp.structures ) > 0 )
	t.assertTrue( isinstance( rsp.structures[0], LocationStructure ) )
	return rsp.structures[0]

@testModule
def retrieveResource ( t, path : 'Storage instance path' ):
	'''Retrieve storage instance.'''
	rsp = t.request( 'GET', path )
	t.assertEqual( rsp.status, 200 )
	
	kind = next( filter( lambda x: isinstance( x, KindStructure ), rsp.structures ) )
	t.assertEqual( kind.term, 'storage' )

@testModule
def createCustomResource ( t, kind : 'Kind to create', structures : 'Additional structures' = None ) -> 'Created instance':
	'''Create a resource instance.'''
	if not kind:
		t.fail( 'Missing kind argument.' )
	if not isinstance( mixin, KindStructure ) and not ( isinstance( mixin, CategoryStructure ) and mixin.isKind() ):
		t.fail( 'Invalid kind argument.' )
	
	kind = kind.identity()
	data = [ kind ] + list( structures ) if structures else []
	rsp = t.request( 'POST', '/{0.term}/'.format( kind ), headerData=data )
	
	t.assertEqual( rsp.status, 200 )
	t.assertTrue( len( rsp.structures ) > 0 )
	t.log( 'Resource created:', rsp.structures[0] )
	return rsp.structures[0]