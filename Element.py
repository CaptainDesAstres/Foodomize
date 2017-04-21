#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Element base object'''
import os

class Element:
	'''Element base object'''
	
	def __init__(self, name='Main', coef=1, kind='group'):
		'''initialize Element'''
		# name and kind of element
		self.name = name
		self.kind = kind
		
		# montly coefficient
		if ( type(coef) == int ):
			self.coef = [coef]*12
		else:
			l=len(coef) 
			if l == 12 :
				self.coef = coef
			elif l in [ 6, 4, 3, 2 ]:
				l = int(12 / l)
				self.coef = []
				while ( len(coef) != 0 ):
					self.coef.extend( [ coef.pop(0) ] * l )
		
		# array of sub element
		self.sub = []
	
	
	
	
	def __str__(self):
		'''return Element in a string form'''
		return 'Not implemented'
	
	
	
	def menu(self):
		'''Element/group menu'''
		
		while(True):
			os.system('clear')# clear terminal output
			menu = input('Menu ? (h for help):').strip()
		
			if(menu in ['exit', 'o', 'out', 'q', 'quit']):
				break
			elif(menu in ['help', 'h']):
				print('''Help:

	In main menu:
	Type:                    To:
	h or help                Get some help
	q or quit                Quit the application
	''')
				input('Press enter to quit Help')
	

