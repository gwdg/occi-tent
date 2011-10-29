from . import testModule

@testModule
def example ( t, param1 : 'Some parameter', param2 : 'Some other parameter' = 'Actually optional..' ):
	t.log( param1 )
	t.log( param2 )
	t.assertTrue( False )

@testModule
def another_example ( t, param1 : 'Some parameter'):
	t.log( param1 )
	t.fail( 'Yes, please.' )