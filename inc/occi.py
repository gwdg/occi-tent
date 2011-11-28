#!/usr/bin/env python3
'''
OCCI rendering structures.
'''

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import urllib.parse, urllib.request
import re

__all__ = [
		'OCCIStructure',
		'AttributeStructure', 'LocationStructure',
		'CategoryStructure', 'MixinStructure', 'KindStructure', 'ActionStructure',
		'LinkStructure' ]

def stripQuotes ( text, quotesRequired = False ):
	'''Strips leading and trailing quotes from the given string.'''
	if text[0] == '"' and text[-1] == '"':
		return text[1:-1]
	elif quotesRequired:
		raise ValueError( 'String is required to be enquoted.' )
	return text


class OCCIStructure:
	headerName = ''

	def __str__ ( self ):
		return self.headerName + ': ' + self.__repr__()
	
	@classmethod
	def parse ( cls, line, strict = False ):
		raise NotImplemented()
	
	def __ne__ ( self, other ):
		return not self.__eq__( other )


class AttributeStructure ( OCCIStructure, dict ):
	headerName = 'X-OCCI-Attribute'

	def __repr__ ( self ):
		return ', '.join( key + '=' + value for key, value in self.items() )

	@classmethod
	def parse ( cls, line, strict = False ):
		if line.startswith( cls.headerName ):
			line = line[len( cls.headerName ) + 1:]
		
		self = cls.__new__ ( cls )
		for attribute in line.split( ',' ):
			if key.split() == '':
				continue
			
			key, value = attribute.split( '=' )
			self[ key.strip() ] = value.strip()
		
		return self


class LocationStructure ( OCCIStructure, list ):
	headerName = 'X-OCCI-Location'

	def __repr__ ( self ):
		return ', '.join( self )
	
	@classmethod
	def parse ( cls, line, strict = False ):
		if line.startswith( cls.headerName ):
			line = line[len( cls.headerName ) + 1:]
		elif line.startswith( 'Location:' ):
			line = line[9:]
		
		self = cls.__new__ ( cls )
		for location in line.split( ',' ):
			if location.split() == '':
				continue
			
			self.append( location.strip() )
		
		return self


class CategoryStructure ( OCCIStructure ):
	headerName = 'Category'
	categoryClass = None

	def __init__ ( self, term, scheme ):
		self.term = term
		self.scheme = scheme
		self.title = None
		self.rel = None
		self.location = None
		self.attributes = []
		self.actions = []
	
	def addAttribute ( self, name, immutable = False, required = False ):
		properties = set()
		if immutable:
			properties.add( 'immutable' )
		if required:
			properties.add( 'required' )
		self.attributes.append( ( name, properties ) )
	
	def __repr__ ( self ):
		l = [ self.term, 'scheme="' + self.scheme + '"', 'class="' + self.categoryClass + '"' ]

		if self.title:
			l.append( 'title="' + self.title + '"' )
		if self.rel:
			l.append( 'rel="' + self.rel + '"' )
		if self.location:
			l.append( 'location="' + self.location + '"' )
		
		if self.attributes:
			attrs = []
			for name, properties in self.attributes:
				if len( properties ) == 0:
					attrs.append( name )
				else:
					attrs.append( name + '{' + ' '.join( properties ) + '}' )
			l.append( 'attributes="' + ' '.join( attrs ) + '"' )
		
		if self.actions:
			l.append( 'actions="' + ' '.join( self.actions ) + '"' )
		
		return '; '.join( l );
	
	def __eq__ ( self, other ):
		return other and self.categoryClass == other.categoryClass and self.term == other.term and self.scheme == self.scheme
	
	def __hash__ ( self ):
		return hash( ( self.categoryClass, self.term, self.scheme ) )
	
	@classmethod
	def parse ( cls, line, strict = False ):
		if line.startswith( cls.headerName ):
			line = line[len( cls.headerName ) + 1:]
		
		term, *parts = line.split( ';' )
		parts = dict( list( part.split( '=' ) for part in map( lambda x: x.strip(), parts ) if part ) )

		try:
			parts['class'] = stripQuotes( parts['class'] )
			if parts['class'] == 'mixin':
				self = MixinStructure.__new__( MixinStructure )
			elif parts['class'] == 'kind':
				self = KindStructure.__new__( KindStructure )
			elif parts['class'] == 'action':
				self = ActionStructure.__new__( ActionStructure )
			else:
				self = cls.__new__( cls )
			
			self.term = term.strip()
			self.scheme = stripQuotes( parts['scheme'], quotesRequired=strict )
			del parts['class'], parts['scheme']
		except KeyError as e:
			raise TypeError( 'Invalid category structure: `{0}` key is missing.'.format( *e.args ) )
		
		self.title = None
		self.rel = None
		self.location = None
		self.attributes = []
		self.actions = []

		if 'title' in parts:
			self.title = stripQuotes( parts['title'], quotesRequired=strict )
			del parts['title']
		
		if 'rel' in parts:
			self.rel = stripQuotes( parts['rel'], quotesRequired=strict )
			del parts['rel']
		
		if 'location' in parts:
			self.location = stripQuotes( parts['location'], quotesRequired=strict )
			del parts['location']
		
		if 'attributes' in parts:
			validProperties = set( ( 'immutable', 'required' ) )
			# TODO: Replace re.find with re.split to not skip invalid parts of the string.
			for name, properties in re.findall( '(?:([^ {]+)(?:{([^}]+)})?)', stripQuotes( parts['attributes'], quotesRequired=strict ) ):
				props = set( properties.split() )
				if strict and len( props - validProperties ) > 0:
					raise ValueError( 'Invalid category structure: Unknown attribute properties found (`{0}`).'.format( '`, `'.join( props - validProperties ) ) )
				self.attributes.append( ( name.strip(), props & validProperties ) )
			del parts['attributes']
		
		if 'actions' in parts:
			self.actions = stripQuotes( parts['actions'], quotesRequired=strict ).split()
			del parts['actions']
		
		if strict and len( parts ) > 0:
			raise ValueError( 'Invalid category structure: Unknown keys found (`{0}`).'.format( '`, `'.join( parts.keys() ) ) )
		else:
			return self
	
	def identity ( self ):
		'''Clone the object, and remove all properties not relevant for the identity.'''
		clone = CategoryStructure.__new__( type( self ) )
		clone.term = self.term
		clone.scheme = self.scheme
		return clone
	
	def isMixin ( self ):
		return self.categoryClass == MixinStructure.categoryClass
	
	def isKind ( self ):
		return self.categoryClass == KindStructure.categoryClass

	def isAction ( self ):
		return self.categoryClass == ActionStructure.categoryClass


class MixinStructure ( CategoryStructure ):
	categoryClass = 'mixin'


class KindStructure ( CategoryStructure ):
	categoryClass = 'kind'


class ActionStructure ( CategoryStructure ):
	categoryClass = 'action'


class LinkStructure ( OCCIStructure ):
	headerName = 'Link'

	def __init__ ( self, link, rel ):
		self.link = link
		self.rel = rel
		self.selfLink = None
		self.category = None
		self.attributes = []
		self.actions = []

	def __repr__ ( self ):
		l = [ '<' + self.link + '>', 'rel="' + self.rel + '"' ]		

		if self.selfLink:
			l.append( 'self="' + self.selfLink + '"' )
		if self.category:
			l.append( 'category="' + self.category + '"' )
		
		for name, value in self.attributes.items():
			l.append( name + '="' + value + '"' )
		
		return '; '.join( l );
	
	def __eq__ ( self, other ):
		return other and self.link == other.link and self.rel == other.rel
	
	def __hash__ ( self ):
		return hash( ( self.link, self.rel ) )

	@classmethod
	def parse ( cls, line, strict = False ):
		if line.startswith( cls.headerName ):
			line = line[len( cls.headerName ) + 1:]
		
		parts = line.split( ';' )
		link = parts.pop( 0 ).strip()[1:-1]
		parts = dict( map( lambda x: x.strip(), part.split( '=' ) ) for part in parts )

		try:
			self = cls.__new__( cls )
			self.link = link
			self.rel = stripQuotes( parts['rel'], quotesRequired=strict )
			del parts['rel']
		except KeyError as e:
			raise TypeError( 'Invalid link structure: `{0}` key is missing.'.format( *e.args ) )
		
		self.selfLink = None
		self.category = None
		self.attributes = []
		self.actions = []
		
		if 'self' in parts:
			self.selfLink = stripQuotes( parts['self'], quotesRequired=strict )
			del parts['self']
		
		if 'category' in parts:
			self.category = stripQuotes( parts['category'], quotesRequred=strict )
			del parts['category']
		
		self.attributes = {}
		for name, value in parts.items():
			self.attributes[name] = stripQuotes( value )
		
		return self