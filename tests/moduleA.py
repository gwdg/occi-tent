from . import testModule

@testModule
def example ( t, param1 : 'Some parameter', param2 : 'Some other parameter' = 'Actually optional..' ):
	t.log( "example" )
	print( param1 )
	print( param2 )
	t.log( "/example" )

@testModule
def another_example ( t, param1 : 'Some parameter'):
	t.log( "another_example" )
	print( param1 )
	t.log( "/another_example" )