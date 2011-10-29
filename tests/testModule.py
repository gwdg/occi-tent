from . import testModule

@testModule
def anotherTest ( t ):
	t.log( 'This is inside the test!' )
	t.assertTrue( True )
	t.assertFalse( False )
	t.assertEqual( 2, 2.0 )