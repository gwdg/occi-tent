#!/usr/bin/env python3
'''
OCCI core tests: Mixin-related operations.
'''

import random

from . import testModule, OCCIError
from inc.occi import *

@testModule
def addMixin ( t, mixin : 'Custom mixin to add' = None ) -> 'Created mixin':
	'''Add mixin.'''
	if mixin:
		if not isinstance( mixin, MixinStructure ) and not ( isinstance( mixin, CategoryStructure ) and mixin.isMixin() ):
			t.fail( 'Invalid mixin argument.' )
	else:
		mixin = MixinStructure( 'tent_test_mixin', 'http://example.com/occi-tent/tent_custom_mixin#' )
		mixin.title = 'OCCI tent test mixin'
		mixin.location = '/occi-tent/tent_custom_mixin/'
	
	rsp = t.request( 'POST', '/-/', headerData=( mixin, ) )
	t.assertEqual( rsp.status, 200 )
	t.log( 'Mixin created:', mixin )
	
	return mixin

@testModule
def addProviderMixin ( t ):
	'''Try to add a provider defined mixin, is supposed to fail.'''
	# only known defined mixin is the IP network.
	mixin = MixinStructure( 'ipnetwork', 'http://schemas.ogf.org/occi/infrastructure/network#' )
	try:
		rsp = t.request( 'POST', '/-/', headerData=( mixin, ) )
	except OCCIError as e:
		t.assertEqual( e.status, 403 ) # HTTP 403: Forbidden
	else:
		t.log( 'Mixin created:', mixin )
		t.fail( 'Mixin was created although it is a provider-defined mixin.' )

@testModule
def addCollidingMixin ( t ):
	'''Try adding a mixin that already exists.'''
	# find available mixins
	rspQuery = t.request( 'GET', '/-/' )
	mixin = random.choice( tuple( filter( lambda s: isinstance( s, MixinStructure ), rspQuery.structures ) ) )
	
	try:
		rsp = t.request( 'POST', '/-/', headerData=( mixin, ) )
	except OCCIError as e:
		t.assertEqual( e.status, 403 ) # HTTP 403: Forbidden
	else:
		t.log( 'Mixin created:', mixin )
		t.fail( 'Mixin was created although it was already existing.' )

@testModule
def removeMixin ( t, mixin : 'Mixin to remove' ):
	'''Remove mixin.'''
	if not mixin:
		t.fail( 'Missing mixin argument.' )
	if not isinstance( mixin, MixinStructure ) and not ( isinstance( mixin, CategoryStructure ) and mixin.isMixin() ):
		t.fail( 'Invalid mixin argument.' )
	
	mixin = mixin.identity()
	rsp = t.request( 'DELETE', '/-/', headerData=( mixin, ) )
	t.assertEqual( rsp.status, 200 )
	t.log( 'Mixin removed:', mixin )

@testModule
def removeProviderMixing ( t ):
	'''Try to remove a provider defined mixin, is supposed to fail.'''
	# only known defined mixin is the IP network.
	mixin = MixinStructure( 'ipnetwork', 'http://schemas.ogf.org/occi/infrastructure/network#' )
	try:
		rsp = t.request( 'DELETE', '/-/', headerData=( mixin, ) )
	except OCCIError as e:
		t.assertEqual( e.status, 403 ) # HTTP 403: Forbidden
	else:
		t.log( 'Mixin removed:', mixin )
		t.fail( 'Mixin was removed although it is a provider-defined mixin.' )

@testModule
def removeNonExistantMixin ( t ):
	'''Try to remove a mixin that does not exist.'''
	# generate mixin with partly randomized name to avoid any conflicts
	mixinName = 'tent_test_mixin_that_should_not_exist_anywhere_' + str( random.randrange( 0xFFFFFFFF ) )
	mixin = MixinStructure( mixinName, 'http://example.com/occi-tent/tent_custom_mixin#' )
	mixin.title = 'OCCI tent test mixin'
	mixin.location = '/occi-tent/' + mixinName + '/'
	
	try:
		rsp = t.request( 'DELETE', '/-/', headerData=( mixin, ) )
	except OCCIError as e:
		t.assertEqual( e.status, 403 ) # HTTP 403: Forbidden
	else:
		t.log( 'Mixin removed:', mixin )
		t.fail( 'Mixin was removed although it was very unlikely that it existed.' )