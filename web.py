#!/usr/bin/env python3
'''
OCCI tent web interface server.
'''

from inc.tent import Tent
from http.server import HTTPServer, BaseHTTPRequestHandler
import glob, sys, threading, webbrowser

class TentRequestHandler ( BaseHTTPRequestHandler ):
	server_version = 'TentWeb/1.0'
	configFile = 'config.yaml'
	
	def initTent ( self ):
		return Tent( self.configFile )
	
	def GET_main ( self, path ):
		body = []
		body.append( '<h1>Tent web interface</h1>' )
		body.append( '<h2>Actions</h2>' )
		body.append( '<ul>' )
		body.append( '  <li><a href="/modules">Test module overview</a></li>' )
		body.append( '  <li><a href="/logs">Test suite logs</a></li>' )
		body.append( '  <li><a href="/cases/SUITENAMEHERE">Test suite, test cases</a></li>' )
		body.append( '  <li><a href="/shutdown">Shutdown web interface</a></li>' )
		body.append( '</ul>' )
		self.sendHtmlResponse( body )
	
	def GET_shutdown ( self, path ):
		body = '<h1>Tent web interface</h1>\n<p>Shutting down…</p>'
		self.sendHtmlResponse( body )
		
		print( 'Shutdown requested, shutting down...' )
		threading.Thread( name='TentShutdownThread', target=self.server.shutdown ).start()
	
	def GET_logs ( self, path ):
		body = [ '<h1>Test suite logs</h1>', '<p>Choose test suite:</p>', '<ul>' ]
		
		for suiteName in glob.glob( '*.yaml.log' ):
			body.append( '  <li><a href="/log/{0}">{0}</a></li>'.format( suiteName[:-9] ) )
		
		body.append( '</ul>' )
		self.sendHtmlResponse( body )
	
	def GET_cases ( self, path ):
		tent = self.initTent()
		body = [ '<h1>Test cases of suite: ' + path[0] + '</h1>' ]
		suite = path[0] + '.yaml'
		
		try:
			f = open( suite )
		except IOError:
			body.append( '<p>Invalid suite name.</p>' )
		else:
			body.append( '<ol>' )
			for testCase in tent.loadTestCases( f ):
				body.append( '  <li>' + testCase.title + '</li>' )
			body.append( '</ol>' )
		self.sendHtmlResponse( body )
	
	def GET_log ( self, path ):
		body = [ '<h1>Log of suite: ' + path[0] + '</h1>' ]
		suite = path[0] + '.yaml'
		
		try:
			f = open( suite + '.log' )
		except IOError:
			body.append( '<p>No logs found or invalid suite name.</p>' )
		else:
			logTime = None
			logLines = []
			for line in f.readlines():
				if line.startswith( '==========' ):
					logLines = []
					logTime = line.strip( '\n= ' )
				else:
					logLines.append( line.strip( '\n' ) )
			f.close()
			
			body.append( '<p>Last execution of <strong>{}</strong>: {}'.format( suite, logTime ) + '</p>' )
			body.append( '<pre>\n' + '\n'.join( logLines ) + '</pre>' )
		self.sendHtmlResponse( body )
	
	def GET_modules ( self, path ):
		tent = self.initTent()
		body = [ '<h1>Test module index</h1>' ]
		
		for module in tent.modules:
			body.append( '<h2>' + module['name'] + '</h2>' )
			
			if module['doc']:
				body.append( '<p>' + module['doc'] + '</p>' )
			
			for function in module['functions']:
				body.append( '<h3>' + function['name'] + '</h3>' )
				
				if function['doc']:
					body.append( '<p>' + function['doc'] + '</p>' )
				
				body.append( '<h4>Parameters</h4>' )
				body.append( '<dl>' )
				for param in function['params']:
					body.append( '  <dt>' + param['name'] + '</dt>' )
					
					if param['annotation']:
						body.append( '  <dd>' + param['annotation'] + '</dd>' )
					else:
						body.append( '  <dd><em>Undocumented</em></dd>' )
					
					if param['default']:
						body.append( '  <dd><em>Default value:</em> <code>' + repr( param['default'] ) + '</code></dd>' )
				body.append( '</dl>' )
		self.sendHtmlResponse( body )
	
	def sendStylesheet ( self ):
		body  = b'''
html { font: 12pt sans-serif; padding: 0; background: #EEE; }
body { background: #FFF; border: 1px solid #CCC; margin: 1em; padding: 2em; }
h1 { background: #CCC; margin: -1em; margin-bottom: 0; padding: 0.1em 0.5em; font-style: italic; font-weight: normal; font-weight: 2em; }
h2 { margin: 0.3em -1em 0.1em -1em; }
h3 { margin: 1em 0 0; border-bottom: 1px solid #EEE; font-size: 1.5em; font-weight: normal; }
h4 { margin: 1em 0 0;  }
p, ul, dl { margin: 0.5em 0em; }
ol, ul { padding-left: 1em; }
li { padding-top: 0.2em; }
a { color: #666; }
pre { white-space: pre-wrap; font-size: 0.9em; }'''	
		
		self.send_response( 200 )
		self.send_header( 'Content-Type', 'text/css; charset=utf-8' )
		self.send_header( 'Content-Length', str( len( body ) ) )
		self.end_headers()
		self.wfile.write( body )
	
	# internal handlers & utility functions
	def do_GET ( self ):
		path = self.path.split( '?', 1 )[0].split( '#', 1 )[0]
		
		if path == '/':
			self.send_response( 301 )
			self.send_header( 'Location', '/main' )
			self.end_headers()
			return
		elif path == '/style.css':
			self.sendStylesheet()
			return
		
		action, *remainder = path[1:].split( '/' )
		action = 'GET_' + action.lower()
		
		if hasattr( self, action ):
			getattr( self, action )( remainder )
		else:
			print( 'Unknown handler:', action )
			self.send_error( 404, 'File not found' )
	
	def sendHtmlResponse ( self, htmlBody, title = 'Tent web interface' ):
		body  = b'<!DOCTYPE html>\n<html>\n<head>\n  <meta charset="utf-8" />\n  <title>'
		body += title.encode()
		body += b'</title>\n  <link rel="stylesheet" href="/style.css" type="text/css" />\n</head>\n\n<body>\n'
		
		if isinstance( htmlBody, list ):
			body += b'\n'.join( map( lambda l: b'  ' + ( l.encode() if isinstance( l, str ) else l ), htmlBody ) )
		elif isinstance( htmlBody, str ):
			body += '\n'.join( map( lambda l: '  ' + l, htmlBody.split( '\n' ) ) ).encode()
		else:
			body += b'\n'.join( map( lambda l: b'  ' + l, htmlBody.split( b'\n' ) ) )
		
		body += b'\n</body>\n</html>'
		self.send_response( 200 )
		self.send_header( 'Content-Type', 'text/html; charset=utf-8' )
		self.send_header( 'Content-Length', str( len( body ) ) )
		self.end_headers()
		self.wfile.write( body )

if __name__ == '__main__':
	port = int( sys.argv[1] ) if sys.argv[1:] else 8080
	httpd = HTTPServer( ( '', port ), TentRequestHandler )
	try:
		print( 'Serving on {0}:{1}...'.format( *httpd.socket.getsockname() ) )
		webbrowser.open( 'http://localhost:{0}'.format( port ) )
		httpd.serve_forever()
	except KeyboardInterrupt:
		print( '\nKeyboard interrupt received, shutting down.' )
		httpd.server_close()
		sys.exit( 0 )