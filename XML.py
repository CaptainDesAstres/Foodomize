#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''usefull function for XML'''

class XML:
	''' a class containing usefull method for XML'''
	
	entities = {
				'\'':'&apos;',
				'"':'&quot;',
				'<':'&lt;',
				'>':'&gt;'
				}
	
	
	
	
	
	def encode(txt):
		'''replace XML entities by XML representation'''
		txt.replace('&', '&amp;')
		
		for entity, code in XML.entities.items():
			txt.replace(entity, code)
		
		return txt
	
	
	
	
	
	def decode(txt):
		'''XML representation by the original character'''
		for entity, code in XML.entities.items():
			txt.replace(code, entity)
		
		txt.replace('&amp;', '&')
		
		return txt
