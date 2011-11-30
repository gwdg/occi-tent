#!/usr/bin/env python3
'''
OCCI core tests: Query interface.
'''

import random

from . import testModule, OCCIError
from inc.occi import *

coreStructures = (
	KindStructure( 'entity', 'http://schemas.ogf.org/occi/core#' ), # Entity
	KindStructure( 'link', 'http://schemas.ogf.org/occi/core#' ), # Link
	KindStructure( 'resource', 'http://schemas.ogf.org/occi/core#' ) # Resource
)
infrastructureStructures = (
	KindStructure( 'compute', 'http://schemas.ogf.org/occi/infrastructure#' ), # Compute
	KindStructure( 'network', 'http://schemas.ogf.org/occi/infrastructure#' ), # Network
	KindStructure( 'networkinterface', 'http://schemas.ogf.org/occi/infrastructure#' ), # Network Interface
	KindStructure( 'storage', 'http://schemas.ogf.org/occi/infrastructure#' ), # Storage
	KindStructure( 'storagelink', 'http://schemas.ogf.org/occi/infrastructure#' ), # Storage Link
	MixinStructure( 'ipnetwork', 'http://schemas.ogf.org/occi/infrastructure/network#' ), # IP Network Mixin

	ActionStructure( 'restart', 'http://schemas.ogf.org/occi/infrastructure/compute/action#' ),
	ActionStructure( 'start', 'http://schemas.ogf.org/occi/infrastructure/compute/action#' ),
	ActionStructure( 'stop', 'http://schemas.ogf.org/occi/infrastructure/compute/action#' ),
	ActionStructure( 'suspend', 'http://schemas.ogf.org/occi/infrastructure/compute/action#' ),
	ActionStructure( 'down', 'http://schemas.ogf.org/occi/infrastructure/network/action#' ),
	ActionStructure( 'up', 'http://schemas.ogf.org/occi/infrastructure/network/action#' ),
	ActionStructure( 'down', 'http://schemas.ogf.org/occi/infrastructure/networkinterface/action#' ),
	ActionStructure( 'up', 'http://schemas.ogf.org/occi/infrastructure/networkinterface/action#' ),
	ActionStructure( 'down', 'http://schemas.ogf.org/occi/infrastructure/storagelink/action#' ),
	ActionStructure( 'up', 'http://schemas.ogf.org/occi/infrastructure/storagelink/action#' ),
	ActionStructure( 'backup', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' ),
	ActionStructure( 'offline', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' ),
	ActionStructure( 'online', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' ),
	ActionStructure( 'resize', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' ),
	ActionStructure( 'snapshot', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' )
)

@testModule
def availability ( t ):
	'''Test the availability of the OCCI query interface.'''
	try:
		rsp = t.request( 'GET', '/-/' )
	except OCCIError as e:
		g.fail( 'OCCI query interface failed with status code ' + e.status )
	else:
		t.assertTrue( len( rsp.structures ) > 0 )
		rsp.close()

@testModule
def builtinStructures ( t, testInfrastructureTypes : 'Test for infrastructure types' = True ):
	'''Test the availability of the built-in OCCI types.'''
	rsp = t.request( 'GET', '/-/' )
	t.log( len( rsp.structures ), 'structures found.' )
	t.assertTrue( len( rsp.structures ) > 0 )
	
	for structure in coreStructures:
		t.assertIn( structure, rsp.structures )
	
	if testInfrastructureTypes:
		for structure in infrastructureStructures:
			t.assertIn( structure, rsp.structures )

@testModule
def fixedFilter ( t ):
	'''Test the query interface filter using a fixed filter.'''
	# subset of built-in structures
	data = set( (
		KindStructure( 'networkinterface', 'http://schemas.ogf.org/occi/infrastructure#' ),
		ActionStructure( 'backup', 'http://schemas.ogf.org/occi/infrastructure/storage/action#' ) ) )
	
	rsp = t.request( 'GET', '/-/', headerData=data )
	t.assertEqual( len( rsp.structures ), len( data ) )
	structureSet = set( rsp.structures )
	t.assertEqual( len( structureSet ), len( data ) )
	t.assertEqual( structureSet, data )

@testModule
def randomFilter ( t ):
	'''Test the query interface filter by first requesting a full discovery and randomly selecting a subset.'''
	rspFull = t.request( 'GET', '/-/' )
	data = set( random.sample( rspFull.structures, 4 ) )
	t.log( 'Active filter:', ', '.join( map( lambda s: '{}/{}'.format( s.categoryClass, s.term ), data ) ) )
	
	rsp = t.request( 'GET', '/-/', headerData=data )
	t.assertEqual( len( rsp.structures ), len( data ) )
	t.assertEqual( set( rsp.structures ), data )