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
		self.kind = kind # group, dishes, dish, variant or ingredient
		
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

	In menu:
	Type:                    To:
	n on new                 in a group, create a group or a dish group
	                         in a dish group, create a dish
	                         in a dish, create a variant
	                         in a variant, create an additionnal ingredient
	h or help                Get some help
	q or quit                Quit the application
	''')
				input('Press enter to quit Help')
			elif[menu in [ 'n', 'new' ] ]:
				self.add()
	
	
	def add(self):
		'''Element adding menu'''
		os.system('clear')# clear terminal output
		
		# print menu title
		if self.kind == 'group':
			print('Add a new group to \''+self.name+'\' group list:')
			kind = input('type \'d\' or \'dishes\' to add a dishes group or anything else to create a standart group').strip().lower() in ['d', 'dishes']
			if kind:
				kind = 'dishes'
			else:
				kind = 'group'
			
		elif self.kind == 'dishes':
			print('Add a new dish to \''+self.name+'\' dishes group :')
			kind = 'dish'
			
		elif self.kind == 'dish':
			print('Add a new variant to \''+self.name+'\' dish :')
			kind = 'variant'
			
		elif self.kind == 'variant':
			print('Add a new additional ingredient to \''+self.name+'\' variant :')
			kind = 'ingredient'
			
		
		
		# get a name:
		while True :
			name = input('choose a name:').strip().lower().capitalize()
			if name == '':
				return
			elif name == 'Main':
				print('«Main» is a reserved name. choose anything else!')
			else:
				break
		
		
		
		
		
	

