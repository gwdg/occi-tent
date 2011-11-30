#!/usr/bin/env python3
'''
OCCI core tests: Namespace path operations.
'''

import random

from . import testModule, OCCIError
from inc.occi import *

@testModule
def hierarchyState ( t, path, acceptUriList : 'Use uri-list accept header' = False ):
	'''Retrieve namespace hierarchy state.'''
	t.assertEqual( hierarchyPath[0], '/', msg='Invalid path argument' )
	t.assertEqual( hierarchyPath[-1], '/', msg='Invalid path argument' )
	accept = 'text/uri-list' if acceptUriList else None
	rsp = t.request( 'GET', path, accept=accept )
	
	t.assertTrue( rsp.contentType, 'text/uri-list' )
	t.log( len( rsp.uris ), 'URIs found.' )
	t.assertTrue( len( rsp.uris ) > 0 )

@testModule
def hasInstances ( t, path ):
	'''Check that instances exist below path.'''
	rsp = t.request( 'GET', path )
	t.assertEqual( rsp.status, 200 )
	t.assertTrue( len( rsp.structures ) > 0 )

@testModule
def retrieveInstances ( t, hierarchyPath ):
	'''Retrieve insances below path.'''
	t.assertEqual( hierarchyPath[0], '/', msg='Invalid path argument' )
	t.assertEqual( hierarchyPath[-1], '/', msg='Invalid path argument' )
	rsp = t.request( 'GET', hierarchyPath )

@testModule
def deleteInstances ( t, hierarchyPath ):
	'''Delete all instances below path.'''
	t.assertEqual( hierarchyPath[0], '/', msg='Invalid path argument' )
	t.assertEqual( hierarchyPath[-1], '/', msg='Invalid path argument' )
	rsp = t.request( 'DELETE', hierarchyPath )