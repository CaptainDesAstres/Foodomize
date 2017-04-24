#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Element base object'''
import os, re
from math import ceil
from XML import XML

class Element:
	'''Element base object'''
	
	def __init__(self,
					name = 'Main',
					coef = 1,
					kind = 'group'
					):
		'''initialize Element'''
		# name and kind of element
		self.name = name
		self.kind = kind # group, dishes, dish, variant or ingredient
		
		self.description = ''
		self.recipe = ''
		self.ingredients = []
		self.extra = []
		self.accompaniments = []
		self.related = []
		
		
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
	
	
	
	
	
	def menu(self):
		'''Element/group menu'''
		page = 0
		quit = False
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.sub) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.print(page)
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if(self.name == 'Main'):
					if(self.save()):
						return True
					else:
						if( input('Quit confirmation (type y or yes):').strip().lower() in [ 'y', 'yes' ] ):
							return True
				elif( menu[0].isupper() ):
					return True
				else:
					return False
				
			elif(menu in ['help', 'h']):
				
				if(self.name == 'Main'):
					quitHelp = '''
q or quit                Quit the app (automatically save before)'''
				else:
					quitHelp = '''
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)'''
				
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 in a group, create a group or a dish group
                         in a dish group, create a dish
                         in a dish, create a variant

in a Variant of a dish:
n or new                 Add an ingredient
i or ingredient          access ingredients menu
e or extra               access extra ingredients menu
a or accompaniment       access accompaniments menu

h or help                Get some help'''+quitHelp)
				
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
				
			if self.kind == 'variant':
				if( menu in [ 'i', 'ingredient' ] ):
					quit = self.manageIngredient()
					
				elif( menu in [ 'e', 'extra' ] ):
					quit = self.manageExtra()
					
			elif (menu == 'desc'):
				self.editDescription()
			else:
				try:
					menu = int(menu)
				except Exception as e:
					continue
				
				if menu < len( self.sub ):
					quit = self.sub[menu].menu()
					
			if(quit is True):
				if self.name != 'Main':
					return True
				else:
					# save before to quit
					if(self.save()):
						return True
					else:
						if( input('Quit confirmation (type y or yes):').strip().lower() in [ 'y', 'yes' ] ):
							return True
	
	
	
	
	def print (self, page=0):
		'''print Element info as displayed in menu'''
		print('			'+self.name+' menu')
		
		# print description
		if self.name != 'Main':
			if self.description == '':
				print('No description. type "desc" to add one.\n')
			else:
				if len(self.description) < 500:
					print(self.description+'\n')
				else:
					print(self.description[0:500]+'…\n')
		
		if self.kind == 'variant':
			# print ingredients
			if( len(self.ingredients) == 0 ):
				print('Ingredients: No ingredient. Type «n» or «new» to add one.')
			else:
				ingredients = ''
				for ing in self.ingredients:
					ingredients += ing[0]+', '
				
				if len(ingredients) > 500:
					ingredients = ingredients[0:498]+'…'
				else:
					ingredients = ingredients[0:-2]
				
				print('Ingredients: '+ingredients)
			
			
			# print extra ingredients
			if( len(self.extra) != 0 ):
				ingredients = ''
				for ing in self.extra:
					ingredients += ing[0]+', '
				
				if len(ingredients) > 500:
					ingredients = ingredients[0:498]+'…'
				else:
					ingredients = ingredients[0:-2]
				
				print('Extra ingredients: '+ingredients)
			
			
			# print accompaniments
			if( len(self.accompaniments) == 0 ):
				print('Accompaniments: No accompaniment suggested. Type «a» or «accompaniment» to access menu.')
			else:
				accompaniments = ''
				for acc in self.accompaniments:
					accompaniments += acc[0]+', '
				
				if len(ingredients) > 500:
					accompaniments = accompaniments[0:498]+'…'
				else:
					accompaniments = accompaniments[0:-2]
				
				print('Accompaniments: '+accompaniments)
			
		else:
			self.printList( page )
	
	
	
	
	def load(self, xml):
		'''load list from xml'''
		# get sub list
		sub = xml.find('sub')
		
		desc = xml.get('description')
		if desc != None:
			self.description = XML.decode( desc )
			
		
		if sub is not None:
			for el in sub:
				# get kind, name, coef
				kind = el.tag
				name = XML.decode( el.get('name') )
				coef = list(map( int, el.get('coef').split(',') ))
				
				# load sub
				self.sub.append( Element( name, coef, kind ) )
				self.sub[-1].load(el)
		
		# load ingredient if specified
		ings = xml.find('ingredients')
		if ings is not None:
			for el in ings:
				name = XML.decode( el.get('name') )
				amount = XML.decode( el.get('amount') )
				
				self.ingredients.append( (name, amount) )
		
		
		
		# load extra ingredient if specified
		extra = xml.find('extra')
		if extra is not None:
			for el in extra:
				name = XML.decode( el.get('name') )
				amount = XML.decode( el.get('amount') )
				
				self.extra.append( (name, amount) )
	
	
	
	def save(self):
		'''save the list in app directory'''
		path = os.path.realpath(__file__+'/..')
		# check path permission
		if os.path.exists(path+'/foodList'):
			if not os.access(path+'/foodList', os.W_OK):
				print('Error, acces denied. can\'t save!')
				return False
		elif(not os.access( path, os.W_OK ) ):
			print('Error, acces denied. can\'t save!')
			return False
		path += '/foodList'
		
		xml = self.toxml()
		
		with open(path,'w') as output:
			output.write(xml)
		
		return True
	
	
	
	
	def toxml(self):
		'''return thi object in xml'''
		xml = ''
		if(self.name == 'Main'):
			xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
		
		xml += '<'+self.kind+' name="'+\
				XML.encode(self.name)+'" coef="'+\
				','.join( map( str, self.coef ) ) +'" '
		
		if self.description != '':
			xml += 'description="'+XML.encode(self.description) +'" '
		
		xml += '>\n'
		
		# export sub element
		if len(self.sub)>0:
			xml += '<sub>\n'
			for el in self.sub:
				xml += el.toxml()
			xml += '</sub>\n'
		
		
		# export ingredients
		if len(self.ingredients)>0:
			xml += '<ingredients>\n'
			for el in self.ingredients:
				xml += '\t<ingredient name="'\
							+XML.encode(el[0])+'" amount="'\
							+XML.encode(el[1])+'" />\n'
			xml += '</ingredients>\n'
		
		
		# export extra ingredients
		if len(self.extra)>0:
			xml += '<extra>\n'
			for el in self.extra:
				xml += '\t<ingredient name="'\
							+XML.encode(el[0])+'" amount="'\
							+XML.encode(el[1])+'" />\n'
			xml += '</extra>\n'
		
		
		xml += '</'+self.kind+'>\n'
		
		return xml
	
	
	
	
	def add(self, kind = ''):
		'''Element adding menu'''
		os.system('clear')# clear terminal output
		
		# print menu title
		if kind == 'extra':
			print('Add a new extra ingredient to \''+self.name+'\' variant :')
			
		elif self.kind == 'group':
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
			print('Add a new ingredient to \''+self.name+'\' variant :')
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
		
		# get coefficient or amount
		while True:
			if kind in [ 'ingredient', 'extra' ]:
				ask = 'amount'
			else:
				ask = 'coefficient(s)'
			
			coef = input('Specify '+ask+' (h for help, q to quit):')
			
			if coef in ['q', 'quit', 'c', 'cancel']:
				return
				
			elif coef in [ 'h', 'help' ] :
				if kind in [ 'ingredient', 'extra' ]:
					print('''Amount help

Amount of ingredient for the recipe. You can press enter with empty string or specify quantity as you wish.''')
				else:
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
				
			elif kind in [ 'ingredient', 'extra' ]:
					break
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
		
		if kind == 'ingredient':
			self.ingredients.append( (name, coef) )
		elif kind == 'extra':
			self.extra.append( (name, coef) )
		else:
			self.sub.append( Element(name,
					coef,
					kind
					) )
	
	
	
	
	def manageIngredient(self):
		'''the menu to see and edit ingrédients list'''
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.ingredients) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.printList( page, self.ingredients )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return True
				else:
					return False
				
			elif(menu in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 Add an  ingredient

h or help                Get some help''')
				
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
			
	
	
	
	
	def manageExtra(self):
		'''the menu to see and edit extra ingrédients list'''
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.extra) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.printList( page, self.extra )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return True
				else:
					return False
				
			elif(menu in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 create an extra ingredient

h or help                Get some help''')
				
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
				self.add(kind = 'extra')
			
	
	
	
	
	def freeName(self, name, tupleList = None):
		'''check if a sub element already use the name.'''
		if tupleList is None:
			for el in self.sub:
				if el.name == name:
					return False
		else:
			for el in tupleList:
				if el[0] == name:
					return False
		
		return True
	
	
	
	
	def printList(self, page, li = None ):
		''' print part of the sub element list'''
		if li == None:
			li = self.sub
		
		# title
		print('		«'+self.name+'» list:\n')
		
		# empty list
		length = len(li)
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
			if(type (li[i]) is Element):
				line = li[i].name
				
				# limit name size
				if len(line) > 29:
					line = line[0:29] + '…'
			elif(type (li[i]) is tuple):
				if li[i][1] == '':
					line = li[i][0]
				else:
					line = li[i][1]+' of '+li[i][0]
			
			# print name
			print(str(i)+'- '+line)
			i+=1
	
	
	
	
	def editDescription(self):
		'''edit description'''
		if self.name=='Main':
			return
		
		print('Edit «'+self.name+'» description')
		
		# print current description
		if(self.description == ''):
			print('Actually no description')
		else:
			print('Current description:'+self.description+'\n')
		
		# get new description
		desc = input('Type the new description or nothing to cancel (only 500 usefull characters):\n').strip()
		
		#apply change
		if (desc != ''):
			self.description = desc
		else:
			if (input('Erase old description? (y or yes):').strip().lower()
						in [ 'y', 'yes' ] ) :
				self.description = ''
			
	

