#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Element base object'''
import os, re
from math import ceil
form XML import XML

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
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.sub) / 15)
			if (page > maxPage):
				page = maxPage
			
			self.printSubList( page )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu in ['exit', 'o', 'out', 'q', 'quit']):
				self.save()
				break
				
			elif(menu in ['help', 'h']):
				save = ''
				if(self.name == 'Main'):
					save = '(automatically save before)'
				
				print('''Help:

	In menu:
	Type:                    To:
	< or -                   Previous 15 elements of the list
	> or +                   Next 15 elements of the list
	empty input              Same thing, back to first page when out of range
	n or new                 in a group, create a group or a dish group
	                         in a dish group, create a dish
	                         in a dish, create a variant
	                         in a variant, create an additionnal ingredient
	h or help                Get some help
	q or quit                Quit the application'''+save)
				
				input('Press enter to continue')
			elif ( menu in [ '-', '<' ] ):
				if page > 0:
					page -= 1
			elif (menu in [ '', '+', '>' ] ):
				maxPage = ceil(len(self.sub) / 15)
				
				if(page < maxPage):
					page += 1
				elif( menu == ''):
					page = 0
				else:
					page = maxPage
				
			elif(menu in [ 'n', 'new' ] ):
				self.add()
	
	
	
	
	def save(self):
		'''save the list in app directory'''
		path = os.path.realpath(__file__+'/..')+'/foodList'
		print (path)
	
	
	
	
	def toxml(self):
		'''return thi object in xml'''
		xml = '<'+self.kind+' name="'+
				XML.encode(self.name)+'" coef="'+
				','.join( map( str, self.coef ) ) +'">'
		
		xml += '<sub>'
		for el in self.sub:
			xml += el.toxml()
		
		xml += '</sub>'
		
		
		xml += '</'+self.kind+'>'
		
		return xml
	
	
	
	
	def add(self):
		'''Element adding menu'''
		os.system('clear')# clear terminal output
		
		# print menu title
		if self.kind == 'group':
			print('Add a new group to \''+self.name+'\' group list:')
			kind = input('type \'d\' or \'dishes\' to add a dishes group or anything else to create a standart group').strip().lower() in ['d', 'dishes']
			
			if kind:
				kind = 'dishes'
				print('Add a dishes group:')
			else:
				kind = 'group'
				print('Add a sub group:')
			
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
			elif '|' in name:
				print('Please, do not use «|» in the name.')
			elif name == 'Main':
				print('«Main» is a reserved name. choose anything else!')
			elif self.freeName(name):
				break
			else:
				print('There is already an element name like this!')
		
		# get coefficient
		while True:
			coef = input('Specify coefficient(s) (h for help, q to quit):')
			
			if coef in ['q', 'quit', 'c', 'cancel']:
				return
				
			elif coef in [ 'h', 'help' ] :
				print('''Coefficient help

Coefficient of an element indicate how much you want it to be randomly choosen.
0 will never be chossen, 2 have 2 times more chance to be choosen than 1. Each coefficient change the luck of other elements to be choosen.
The coefficient MUST ABSOLUTELY BE A POSITIVE INTEGER as greater as you want!

Press enter without typing anything and the coefficint will be 1 for all the year.
Type one number and it will be used all the year.

Type multiple number separated by a space or a / or a - (empty = 0):
With 2 numbers, each define 6 months.
3 numbers = 4 months each
4 numbers = 3 months each
6 numpers = 2 months each
12 numbers = 1 for each month

This maner, it simple to made an element more likely to show up on some time of the year, like winter/summer dishes.
''')
				input('Press enter to continue:')
				
			elif coef == '':
				coef = 1
				break
				
			else:
				coefs = re.split( '-| |/', coef )
				
				if len (coefs) == 1:
					try:
						coef = int(coefs[0])
					except Exception as e:
						print('Error, you\'ve probably type invalid value')
						continue
					break
					
				elif len(coefs) in [ 2, 3, 4, 6, 12 ]:
					coef = []
					noerror = True
					for c in coefs:
						
						if c == '':
							coef.append(0)
							
						else:
							try:
								coef.append( int(c) )
							except Exception as e:
								print('Error, you\'ve probably type an invalid value')
								noerror = False
								break
					
					if noerror:
						break
					
				else:
					print('Error, you must type 1 2 3 4 6 or 12 numbers. ')
		
		self.sub.append( Element(name,
				coef,
				kind
				) )
	
	
	
	
	def freeName(self, name):
		'''check if a sub element already use the name.'''
		for el in self.sub:
			if el.name == name:
				return False
		
		return True
	
	
	
	
	def printSubList(self, page ):
		''' print part of the sub element list'''
		# title
		print('		«'+self.name+'» list:\n')
		
		# empty list
		length = len(self.sub)
		if length == 0:
			print('empty list')
			return
		
		# page limits
		i = page * 15
		end = i+15
		if end > length:
			end = length
		
		# print page list
		while(i < end):
			name = self.sub[i].name
			
			# limit name size
			if len(name) > 29:
				name = name[0:29] + '…'
			
			# print name
			print(str(i)+'- '+name)
			i+=1

