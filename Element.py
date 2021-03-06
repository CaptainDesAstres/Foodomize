#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''Element base object'''
import os, re, subprocess, shutil
from math import ceil
from XML import XML
from random import randint

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
		self.recipe = False
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
	
	
	
	
	def getName(self):
		'''return name (for sorting method)'''
		return self.name
	
	
	
	
	def menu(self, main = None, path = '', parent = None ):
		'''Element/group menu'''
		page = 0
		
		if main is None:
			main = self
		
		if self.name != 'Main':
			if path == '':
				path = self.name
			else:
				path += '|'+self.name
		
		# quit flag 
		#		(
		#		save and quit app,
		#		quit app without saving,
		#		return to main menu
		#		)
		quit = ( False, False, False )
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.sub) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.print(page, main.month)
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if(self.name == 'Main'):
					if(self.save()):
						return
					else:
						if( input('Quit confirmation (type y or yes):').strip().lower() in [ 'y', 'yes' ] ):
							return
				elif( menu[0].isupper() ):
					return ( True, False, False )
				else:
					return ( False, False, False )
				
			elif(menu == 'SAFE'):
				return ( False, True, False )
				
			elif(menu.lower() in ['m', 'main'] and self.name != 'Main'):
				return ( False, False, True )
				
			elif(menu.lower() in ['help', 'h']):
				
				if(self.name == 'Main'):
					quitHelp = '''
q or quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving'''
				else:
					quitHelp = '''
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving
m or main                Return to the main menu'''
				
				print('''Help:

In menu:
Type:                    To:
m or month               change month to use for coefficient for randomization
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 in a group, create a group or a dish group
                         in a dish group, create a dish
                         in a dish, create a variant
name                     edit current element name
c or coef                edit current element coefficients
d N or delete N          Delete sub element with index N
d 0 1 2 3                Delete each sub element listed (0 1 2 and 3)

in a dish or variant:
n or new                 Add an ingredient (in variant only)
i or ingredient          access ingredients menu
e or extra               access extra ingredients menu
a or accompaniment       access accompaniments menu
s or suggest             access suggested meal menu
recipe                   read/edit dish recipe
delete recipe            to delete recipe of this variant

random function: (don't work in variant)
Those function randomly choose a sub element, using there coefficient for the current working month. It start from the current element.
R or RANDOM              randomly choose one of the sub element
r N or random N          randomly and recursivly choose an element, with N as level limit
r or random              randomly and recursivly choose an element without level limit

editor                   Change the default text editor (used to edit recipe)
h or help                Get some help'''+quitHelp)
				
				input('Press enter to continue')
			elif ( menu.lower() == 'editor' ):
				editor = input('''current editor: «'''+main.editor+'''».
type the command to your editor:''').strip()
				
				if(editor != ''):
					main.editor = editor
				
			elif ( menu in [ '-', '<' ] ):
				if page > 0:
					page -= 1
			elif (menu in [ '', '+', '>' ] ):
				maxPage = ceil(len(self.sub) / 15)-1
				
				if(page < maxPage):
					page += 1
				elif( menu == ''):
					page = 0
				else:
					page = maxPage
				
			elif(menu.lower() in [ 'm', 'month' ] ):
				main.changeMonth()
				
			elif(menu.lower() in [ 'c', 'coef' ] and self.name != 'Main'):
				self.editCoef()
				
			elif( menu.lower() == 'name' ):
				if self.name!= 'Main':
					path = self.editName( parent, main, path )
				else:
					input('«Main» menu can\'t be renamed. (Press enter to continue)')
				
			elif(menu.lower() in [ 'n', 'new' ] ):
				self.add()
				self.sub.sort( key = Element.getName )
				
			elif (menu.lower() == 'desc'):
				self.editDescription()
				
			elif menu.lower() in [ 'r', 'random' ]\
					or menu.lower().startswith('r ')\
					or menu.lower().startswith('random ') :
				if len(self.sub)==0:
					input('Foodomize can\'t propose you any sub element from «'+self.name+'»: there is none.')
					continue
				
				# get depth
				if menu in [ 'r', 'random' ]:
					depth = 0
				elif menu in [ 'R', 'RANDOM' ]:
					depth = 1
				else:
					if menu.lower().startswith('r '):
						depth = menu[2:]
					else:
						depth = menu[7:]
					
					# try to convert to int
					try:
						depth = int( depth )
					except Exception as e:
						print('Error: «'+depth+'» can\'t be convert into an integer')
						input('press enter to continue')
						continue
					
					# check the value is valid
					if depth <= 0:
						print('Error: you must specify a positive integer.')
						input('press enter to continue')
						continue
				
				
				self.random( path, depth, main )
				
			elif menu.startswith('delete ') or menu.startswith('d ') :
				if menu.startswith('delete '):
					i = menu[7:].split(' ')
				else:
					i = menu[2:].split(' ')
				
				# get sub element index
				try:
					index = []
					for el in i:
						if el != '':
							index.append( int( el ) )
					
				except Exception as e:
					print('Error: «'+el+'» is not an integer')
					input('press enter to continue')
					continue
				
				# erase index duplicate values
				index = list( set( index ) )
				
				# check index is in the range
				error = False
				names = []
				for i in index:
					if i >= len(self.sub) or i < 0:
						input('No sub element with index '+str(i)+'. press enter to continue.')
						error = True
						break
					else:
						names.append(self.sub[i].name)
				if error:
					continue
				names = ', '.join(names)
				
				# ask to confirm
				if input('Do you realy want to delete «'+names\
						+'» element and their sub element?(type «y» or «yes» to confirm or anything else to cancel)'\
						).lower() not in [ 'y', 'yes']:
					continue
				
				# erase each accompaniments
				index.sort(reverse=True)
				for i in index:
					self.sub[i].erase( path, main )
					self.sub.pop(i)
				
			elif self.kind in ['variant', 'dish'] \
						and menu.lower() in [ 'i', 'ingredient', 'e', 'extra', 
									'a', 'accompaniment', 's', 'suggest', 'recipe',
									'delete recipe'] :
				menu = menu.lower()
				if( menu in [ 'i', 'ingredient' ] ):
					quit = self.manageIngredient()
					
				elif( menu in [ 'e', 'extra' ] ):
					quit = self.manageExtra()
					
				elif( menu in [ 'a', 'accompaniment' ] ):
					quit = self.manageAccompaniment()
					
				elif( menu in [ 's', 'suggest' ] ):
					quit = self.manageRelatedMeal( main, path )
					
				elif( menu == 'recipe'):
					# run editor to see and modify recipe
					try:
						# get recipes directory path or create it
						recipePath = os.path.realpath(__file__+'/../recipes')
						if not os.path.exists(recipePath):
							os.mkdir(recipePath)
						
						recipePath += '/'+path
						
						subprocess.call([main.editor, recipePath])
					except Exception as e:
						print(e)
						input('press enter to ignore this error and continue')
					
					#check there is a saved file for the recipe
					if os.path.exists(recipePath):
						self.recipe = True
					else:
						self.recipe = False
					
				elif( menu == 'delete recipe' and self.recipe):
					if input('Do you realy want to erase this recipe (type y or yes):')\
							not in ['y', 'yes']:
						continue
					
					try:
						# get recipes directory path
						recipePath = os.path.realpath(__file__+'/../recipes')+'/'+path
						
						# delete element recipe
						if os.path.exists(recipePath):
							os.remove(recipePath)
						
						self.recipe = False
						
					except Exception as e:
						print(e)
						input('press enter to ignore this error and continue')
					
			else:
				try:
					menu = int(menu)
				except Exception as e:
					continue
				
				if menu < len( self.sub ) and menu > -1:
					quit = self.sub[menu].menu( main, path, self )
					self.sub.sort( key = Element.getName )
			if(quit[0] is True):
				if self.name != 'Main':
					return quit
				else:
					# save before to quit
					if(self.save()):
						return quit
					else:
						if( input('Quit confirmation (type y or yes):').strip().lower() in [ 'y', 'yes' ] ):
							return quit
			elif(quit[1] is True):
				return quit
			elif(quit[2] is True and self.name != 'Main'):
				return quit
	
	
	
	
	
	def random( self, rootPath, limit, main ):
		'''randomly sub element'''
		# check if there is a limit
		noLimit = ( limit == 0 )
		month = main.month - 1
		root = self.name
		
		# random loop
		again = True
		while again:
			level = self
			i = 0
			path = rootPath
			
			# random level loop
			while( ( noLimit or i < limit ) and len(level.sub) > 0 ):
				# get coefficient sum
				coefSum = 0
				for el in level.sub:
					coefSum += el.coef[ month ]
				
				# get random value
				r = randint( 1, coefSum )
				
				# get the selected sub element
				for el in level.sub:
					r -= el.coef[ month ]
					if r <= 0:
						level = el
						
						# compile the path
						if path == '':
							path += el.name
						else:
							path += '|'+el.name
						
						break
				
				i += 1
			
			again = level.randomMenu( path, root, main )
	
	
	
	
	
	def randomMenu( self, path, root, main ):
		'''random menu to display info about randomly choosen element'''
		month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][main.month - 1]
		
		
		# get ingredients list
		ingredients = ''
		if len(self.ingredients)>0:
			for ing in self.ingredients:
				if ing[1]=='':
					ingredients += ing[0]+', '
				else:
					ingredients += ing[0]+' ('+ing[1]+'), '
			
			ingredients = ingredients[ 0 : -2 ]
		if len(ingredients) > 500:
			shortIngredients = ingredients[0:499]+'…'
		else:
			shortIngredients = ingredients
		
		# get extra ingredients list
		extra = ''
		if len(self.extra)>0:
			for ing in self.extra:
				if ing[1]=='':
					extra += ing[0]+', '
				else:
					extra += ing[0]+' ('+ing[1]+'), '
			
			extra = extra[ 0 : -2 ]
		if len(extra) > 500:
			shortExtra = extra[0:499]+'…'
		else:
			shortExtra = extra
		
		
		# get accompaniments list
		accompaniments = ''
		if len(self.accompaniments)>0:
			for acc in self.accompaniments:
				accompaniments += acc+', '
				
			
			accompaniments = accompaniments[ 0 : -2 ]
		if len(accompaniments) > 500:
			shortAccompaniments = accompaniments[0:499]+'…'
		else:
			shortAccompaniments = accompaniments
		
		
		# get related meal list
		related = ''
		if len(self.related)>0:
			for rel in self.related:
				related += rel.split('|')[-1]+', '
				
			
			related = related[ 0 : -2 ]
		if len(related) > 500:
			shortRelated = related[0:499]+'…'
		else:
			shortRelated = related
		
		
		# get sub element list
		sub = ''
		if len(self.sub)>0:
			for el in self.sub:
				sub += el.name+', '
				
			
			sub = sub[ 0 : -2 ]
		if len(sub) > 500:
			shortSub = sub[0:499]+'…'
		else:
			shortSub = sub
		
		
		while True:
			os.system('clear')
			
			print('			Randomly choose from «'+root+'» list:')
			print('\nRamdomly choosen using '+month+' coefficients.\n')
			print('Foodomize propose you «'+self.name+'»:')
			
			if self.description =='':
				print('No description avaible.\n')
			else:
				description = self.description
				if len(description) > 500:
					description = description[0:499]+'…'
				print(description+'\n')
			
			if(self.kind in [ 'dish', 'variant' ]):
				# display ingrédient list
				if shortIngredients == '':
					print('Ingredients: Unknow')
				else:
					print('Ingredients: '+shortIngredients)
				
				# display ingrédient list
				if shortExtra == '':
					print('Extra ingredients: no one know')
				else:
					print('Extra ingredients: '+shortExtra)
				
				# display accompaniments list
				if shortAccompaniments == '':
					print('Recommended accompaniments: no one know')
				else:
					print('Recommended accompaniments: '+shortAccompaniments)
				
				# display related list
				if shortRelated == '':
					print('Related meal: no one know.\n')
				else:
					print('Related meal: '+shortRelated+'\n')
			
			if shortSub == '':
				print('Sub elements: none')
			else:
				print('Sub elements: '+shortSub)
			
			next = input('\nwhat next? (type «help» for help)').strip()
			if next == '':
				return True
			else:
				upper = next[0].isupper()
			next = next.lower()
			
			if next in [ 'q', 'quit' ]:
				return False
				
			elif next in [ 'h', 'help' ]:
				input('''Random Menu Help:
You're in the random menu, where you can randomly choose element.

press enter without typing anything to randomly choose another element from «'''+root+'''» list or :
Type:                    To:
recipe                   read/edit this element recipe, if there is one
d or desc                see the full description (if truncated)
i or ingredient          see the full ingredients list (if truncated)
e or extra               see the full extra ingredients list (if truncated)
a or accompaniment       see the full accompaniment list (if truncated)
rel or related           see the full related meal list (if truncated)


If the element have sub element, you can use random function on it:
R or RANDOM              randomly choose one of the sub element
r N or random N          randomly and recursivly choose an element, with N as level limit
r or random              randomly and recursivly choose an element without level limit


random related           ramdomly choose one of the related meal
random acc               ramdomly choose one of the accompaniment
random extra             ramdomly choose one of the extra ingredient

q or quit                quit random menu
h or help                read this help

press enter to continue''')
				
			elif next == 'recipe' :
				recipePath = os.path.realpath(__file__+'/../recipes')+'/'+path
				
				if self.recipe and os.path.exists(recipePath):
					try:
						subprocess.call([main.editor, recipePath])
					except Exception as e:
						print(e)
						input('press enter to ignore this error and continue')
				else:
					input('this element have no recipe')
				
			elif next in [ 'd', 'desc']:
				os.system('clear')
				print('			«'+self.name+'» description:\n')
				
				if self.description =='':
					print('There is no description for «'+self.name+'»…')
				else:
					print(self.description)
				
				input('press enter to continue')
			elif next in [ 'i', 'ingredient', 'ing', 'ingredients' ]:
				os.system('clear')
				print('			«'+self.name+'» ingredients:\n')
				
				if ingredients == '':
					print('There is no know ingredient for «'+self.name+'»…')
				else:
					print('Ingredients: '+ingredients)
				
				input('press enter to continue')
				
			elif next in [ 'e', 'extra' ]:
				os.system('clear')
				print('			«'+self.name+'» extra ingredients:\n')
				
				if extra == '':
					print('There is no know extra ingredient for «'+self.name+'»…')
				else:
					print('Extra ingredients: '+extra)
				
				input('press enter to continue')
				
			elif next in [ 'a', 'acc', 'accompaniment', 'accompaniments' ]:
				os.system('clear')
				print('			«'+self.name+'» recommended accompaniments:\n')
				
				if accompaniments == '':
					print('There is no know accompaniment for «'+self.name+'»…')
				else:
					print('Accompaniments: '+accompaniments)
				
				input('press enter to continue')
				
			elif next in [ 'rel', 'related', 's', 'suggest' ]:
				os.system('clear')
				print('			«'+self.name+'» related meal:\n')
				
				if related == '':
					print('There is no know related meal for «'+self.name+'»…')
				else:
					print('Related meals: '+related)
				
				input('press enter to continue')
				
			elif next == 'sub':
				os.system('clear')
				print('			«'+self.name+'» sub elements:\n')
				
				if sub == '':
					print('There is no know sub element in «'+self.name+'»…')
				else:
					print('sub elements: '+sub)
				
				input('press enter to continue')
				
			elif( next.startswith('r') ):
				if next.startswith('r '):
					next = next[2:]
				elif next.startswith('random '):
					next = next[7:]
				elif next in [ 'r', 'random' ]:
					next = ''
				else:
					continue
				
				again = True
				loopMsg = '\nPress enter for a new proposal or type anything to stop:'
				
				if(next in [ 'r', 'rel', 'related', 's', 'suggest' ] ):
					self.randomRelated( main )
					
				elif(next in [ 'a', 'acc', 'accompaniment', 'accompaniments' ] ):
					if len(self.accompaniments)==0:
						input('Foodomize can\'t propose you any accompaniment: this meal have none.')
						continue
					
					while again:
						acc = self.accompaniments[ 
								randint( 0, len(self.accompaniments)-1) ]
						again = input('Foodomize propose you «'+acc+'» as accompaniment for this meal.'+loopMsg).strip() == ''
						
				elif(next in [ 'e', 'extra' ] ):
					if len(self.extra)==0:
						input('Foodomize can\'t propose you to add any ingredient: this meal have none extra ingredient.')
						continue
					
					while again:
						e = self.extra[ 
								randint( 0, len(self.extra)-1) ]
						if e[1] == '':
							again = input('Foodomize propose you to add «'+e[0]+'» to this meal.'+loopMsg).strip() == ''
						else:
							again = input('Foodomize propose you to add «'+e[0]+'»('+e[1]+') to this meal.'+loopMsg).strip() == ''
					
				else:
					if len(self.sub)==0:
						input('Foodomize can\'t propose you any sub element from «'+self.name+'»: there is none.')
						continue
					
					# get random depth
					if next == '':
						if upper:
							limit = 1
						else:
							limit = 0
					else:
						try:
							limit = int( next.strip() )
						except Exception as e:
							input('Error: «'+next+'» can\'t be convert into integer.\nPress enter to continue')
							continue
						
						if limit < 0:
							input('Error: you must specify a positive integer for random.\nPress enter to continue')
							continue
					
					self.random( path, limit, main )
	
	
	
	
	
	def randomRelated(self, main):
		'''randomly propose a meal from this one'''
		if len(self.related)==0:
				input('Foodomize can\'t propose you any related meal: this meal have none.')
				return
		
		# get related list
		month = main.month - 1
		related = []
		coefSum = 0
		for path in self.related:
			related.append( [path, main.getPath(path.split('|'))] )
			coefSum += related[-1][1].coef[month]
		
		again = True
		while again:
			r = randint( 1, coefSum )
			
			for rel in related:
				r -= rel[1].coef[month]
				if r <= 0:
					break
			
			again = rel[1].randomMenu( rel[0], self.name, main )
			
		
	
	
	
	
	
	def erase( self, path, main ):
		'''do all there is to do before deleting the current element'''
		if path == '':
			path = self.name
		else:
			path += '|'+self.name
		
		# erase sub element
		for el in self.sub:
			el.erase( path, main )
		
		# erase reference from related element
		for rel in self.related:
			rel = rel.split('|')
			main.getPath(rel).related.remove( path )
		
		# delete recipe file
		if self.recipe:
			try:
				# get recipes directory path
				recipePath = os.path.realpath(__file__+'/../recipes')+'/'+path
				
				# delete element recipe
				if os.path.exists(recipePath):
					os.remove(recipePath)
			except Exception as e:
				print('error while trying to erase «'+path.split('|')[-1]+'» recipe:')
				print(e)
				input('press enter to ignore this error and continue')
			
	
	
	
	
	
	def editCoef( self ):
		'''edit element coefficients'''
		# get coefficient or amount
		while True:
			os.system('clear')
			
			print('			Edit coefficients for '+self.name+':\n')
			self.printCoef( True )
			
			coef = input('Specify new coefficient(s) (h for help):')
			
			if coef in ['', 'q', 'quit', 'c', 'cancel']:
				return
				
			elif coef in [ 'h', 'help' ] :
				print('''Coefficient help

Coefficient of an element indicate how much you want it to be randomly choosen.
0 will never be chossen, 2 have 2 times more chance to be choosen than 1. Each coefficient change the luck of other elements to be choosen.
The coefficient MUST ABSOLUTELY BE A POSITIVE INTEGER as greater as you want!

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
	
	
	
	
	def changeMonth( self ):
		'''change working month (only use with main element).'''
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		os.system('clear')
		
		print('			Change working month:\n\nCurrent working month: '\
					+months[ self.month-1 ]+'.\n\nType a number between 1 and 12 or the full name of the month.')
		
		while True:
			m = input('Type the wanted working month:').strip()
			
			if m == '':
				return
			
			if m.capitalize() in months:
				self.month = months.index(m.capitalize()) + 1
				return
			else:
				try:
					m = int(m)
					if m > 0 and m < 13:
						self.month = m
						return
					else:
						print('Error, '+str(m)+' is not a valid value')
				except Exception as e:
					print('Error, '+m+' is not a valid value')
					continue
	
	
	
	
	def editName( self, parent, main, oldPath ):
		'''edit Element name'''
		# get a name:
		while True :
			name = input('Choose a new name for «'+self.name+'»:')\
							.strip().lower().title()
			
			# check the name
			if name == '':
				return
				
			elif '|' in name:
				print('Please, do not use «|» in the name.')
				
			elif name == 'Main':
				print('«Main» is a reserved name. choose anything else!')
				
			elif (parent.freeName( name )):
				break
			else:
				print('There is already an element name like this!')
		
		# change name
		self.name = name
		
		# change path
		path = oldPath.split('|')
		path[-1] = name
		newPath = '|'.join( path )
		
		# adapt related meal path
		main.relatedPathInvert( oldPath, newPath )
		
		#change recipe file name
		if self.recipe:
			rep = os.path.realpath(__file__+'/../recipes')
			oldfile = rep+'/'+oldPath
			newfile = rep+'/'+newPath
			
			# change file name
			if os.path.exists(oldfile):
				shutil.move( oldfile, newfile )
		
		
		# return the new path
		return newPath
	
	
	
	
	def relatedPathInvert( self, old, new ):
		'''recursively modify'''
		# change path
		if old in self.related:
			self.related.remove(old)
			self.related.append(new)
		
		# erase double
		while old in self.related:
			self.related.remove(old)
		
		# recursively do it for sub element
		for el in self.sub:
			el.relatedPathInvert( old, new )
		
		
	
	
	
	
	def print (self, page=0, month = None):
		'''print Element info as displayed in menu'''
		print('			'+self.name+' menu')
		m = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month-1]
		
		if self.name != 'Main':
			print('Current working month: '+m+'.\n')
			
			# print coefficient
			self.printCoef(month=month)
			self.printCoef()
			
			# print description
			if self.description == '':
				print('\nNo description. type "desc" to add one.\n')
			else:
				if len(self.description) < 500:
					print('\n'+self.description+'\n')
				else:
					print('\n'+self.description[0:500]+'…\n')
		else:
			print('Current working month: '+m+'.\n')
		
		if self.kind in ['variant', 'dish']:
			# print ingredients
			if( len(self.ingredients) == 0 ):
				print('Ingredients: No ingredient. Type «i» or «ingredient» to access ingredient menu.')
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
			else:
				print('Extra ingredients: No one know. Type «e» or «extra» to access extra ingredient menu.')
			
			
			# print accompaniments
			if( len(self.accompaniments) == 0 ):
				print('Accompaniments: No accompaniment suggested. Type «a» or «accompaniment» to access menu.')
			else:
				accompaniments = ''
				for acc in self.accompaniments:
					accompaniments += acc+', '
				
				if len(ingredients) > 500:
					accompaniments = accompaniments[0:498]+'…'
				else:
					accompaniments = accompaniments[0:-2]
				
				print('Accompaniments: '+accompaniments)
			
			
			# suggest meal
			print('type «s» to see suggested meal with this one')
			
			if(self.recipe):
				print('type «recipe» to see this meal recipe in your editor.\n')
			else:
				print('actually no recipe for this meal. type «recipe» to write one in your prefered editor\n')
		
		if (self.kind != 'variant'):
			if self.kind != 'dish':
				self.printList( page )
			else:
				self.printList( page, title=' variant' )
	
	
	
	
	def load(self, xml):
		'''load list from xml'''
		# get sub list
		sub = xml.find('sub')
		
		if(self.name == 'Main'):
			self.editor = XML.decode(xml.get('editor'))
		
		desc = xml.get('description')
		if desc != None:
			self.description = XML.decode( desc )
		
		self.recipe = xml.get('recipe') == 'True'
		
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
		
		
		
		# load accompaniments if specified
		accs = xml.find('accompaniments')
		if accs is not None:
			for el in accs:
				name = XML.decode( el.get('name') )
				
				self.accompaniments.append( name )
		
		
		
		# load related meals if specified
		related = xml.find('related')
		if related is not None:
			for el in related:
				path = XML.decode( el.get('path') )
				
				self.related.append( path )
	
	
	
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
				','.join( map( str, self.coef ) ) +'" recipe="'+\
				str(self.recipe)+'" '
		
		if(self.name == 'Main'):
			xml += 'editor="'+XML.encode(self.editor) +'" '
		
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
		
		
		# export accompaniments
		if len(self.accompaniments)>0:
			xml += '<accompaniments>\n'
			for el in self.accompaniments:
				xml += '\t<accompaniment name="'\
							+XML.encode(el)+'" />\n'
			xml += '</accompaniments>\n'
		
		
		# export related meal list
		if len(self.related)>0:
			xml += '<related>\n'
			for el in self.related:
				xml += '\t<meal path="'\
							+XML.encode(el)+'" />\n'
			xml += '</related>\n'
		
		
		xml += '</'+self.kind+'>\n'
		
		return xml
	
	
	
	
	def add(self, kind = ''):
		'''Element adding menu'''
		os.system('clear')# clear terminal output
		nameList = None
		
		# print menu title
		if kind == 'extra':
			print('Add a new extra ingredient to \''+self.name+'\' variant :')
			nameList = self.extra
			
		elif kind == 'accompaniment':
			print('Add a new accompaniment to \''+self.name+'\' variant :')
			
			
		elif kind == 'ingredient':
			print('Add a new ingredient to \''+self.name+'\' :')
			nameList = self.ingredients
			
		elif self.kind == 'group':
			print('Add a new group to \''+self.name+'\' group list:')
			kind = input('type \'d\' or \'dish\' to add a dish or anything else to create a sub group of dishes').strip().lower() in ['d', 'dish']
			
			if kind:
				kind = 'dish'
				print('Add a dish:')
			else:
				kind = 'group'
				print('Add a sub dishes group:')
			
		elif self.kind == 'dish':
			print('Add a new variant to \''+self.name+'\' dish :')
			kind = 'variant'
			
		
		
		# get a name:
		while True :
			name = input('choose a name:').strip().lower().title()
			if name == '':
				return
			elif '|' in name or '/' in name:
				print('Please, do not use «|» nor «/» in the name.')
			elif name == 'Main':
				print('«Main» is a reserved name. choose anything else!')
			elif (kind == 'accompaniment' and name not in self.accompaniments
						or self.freeName(name, nameList)):
				break
			else:
				print('There is already an element name like this!')
		
		# get coefficient or amount
		while kind != 'accompaniment':
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
		elif kind == 'accompaniment':
			self.accompaniments.append( name )
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
			
			self.printList( page, self.ingredients, 'ingredients' )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return ( True, False, False )
				else:
					return ( False, False, False )
				
			elif(menu == 'SAFE'):
				return ( False, True, False )
				
			elif(menu.lower() in ['m', 'main']):
				return ( False, False, True )
				
			elif(menu.lower() in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 Add an  ingredient
d N or delete N          delete the ingredient with index N
d 0 1 2 3                delete each ingredient listed (0 1 2 and 3)

h or help                Get some help
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving
m or main                Return to the main menu''')
				
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
				
			elif(menu.lower() in [ 'n', 'new' ] ):
				self.add(kind='ingredient')
				
			elif menu.startswith('delete ') or menu.startswith('d ') :
				if menu.startswith('delete '):
					i = menu[7:].split(' ')
				else:
					i = menu[2:].split(' ')
				
				# get ingredient index
				try:
					index = []
					for el in i:
						if el != '':
							index.append( int( el ) )
					
				except Exception as e:
					print('Error: «'+el+'» is not an integer')
					input('press enter to continue')
					continue
				
				# erase index duplicate values
				index = list( set( index ) )
				
				# check index is in the range
				error = False
				names = []
				for i in index:
					if i >= len(self.ingredients) or i < 0:
						input('No ingredient with index '+str(i)+'. press enter to continue.')
						error = True
						break
					else:
						names.append(self.ingredients[i][0])
				if error:
					continue
				names = ', '.join(names)
				
				# ask to confirm
				if input('do you realy want to delete «'+names+'» ingredient?(press enter to confirm or type anything to cancel)') != '':
					continue
				
				# erase each ingredient
				index.sort(reverse=True)
				for i in index:
					self.ingredients.pop(i)
			
	
	
	
	
	def manageExtra(self):
		'''the menu to see and edit extra ingrédients list'''
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.extra) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.printList( page, self.extra, 'extra ingredients' )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return ( True, False, False )
				else:
					return ( False, False, False )
				
			elif(menu == 'SAFE'):
				return ( False, True, False )
				
			elif(menu.lower() in ['m', 'main']):
				return ( False, False, True )
				
			elif(menu.lower() in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 create an extra ingredient
delete N                 delete the extra ingredient with index N
d 0 1 2 3                delete each extra ingredient listed (0 1 2 and 3)

h or help                Get some help
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving
m or main                Return to the main menu''')
				
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
				
			elif(menu.lower() in [ 'n', 'new' ] ):
				self.add(kind = 'extra')
				
			elif menu.startswith('delete ') or menu.startswith('d ') :
				if menu.startswith('delete '):
					i = menu[7:].split(' ')
				else:
					i = menu[2:].split(' ')
				
				# get extra ingredient index
				try:
					index = []
					for el in i:
						if el != '':
							index.append( int( el ) )
					
				except Exception as e:
					print('Error: «'+el+'» is not an integer')
					input('press enter to continue')
					continue
				
				# erase index duplicate values
				index = list( set( index ) )
				
				# check index is in the range
				error = False
				names = []
				for i in index:
					if i >= len(self.extra) or i < 0:
						input('No extra ingredient with index '+str(i)+'. press enter to continue.')
						error = True
						break
					else:
						names.append(self.extra[i][0])
				if error:
					continue
				names = ', '.join(names)
				
				# ask to confirm
				if input('do you realy want to delete «'+names+'» extra ingredient?(press enter to confirm or type anything to cancel)') != '':
					continue
				
				# erase each extra ingredient
				index.sort(reverse=True)
				for i in index:
					self.extra.pop(i)
	
	
	
	
	def manageAccompaniment(self):
		'''the menu to see and edit accompaniments list'''
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.accompaniments) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.printList( page, self.accompaniments, 'accompaniments' )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return ( True, False, False )
				else:
					return ( False, False, False )
				
			elif(menu == 'SAFE'):
				return ( False, True, False )
				
			elif(menu.lower() in ['m', 'main']):
				return ( False, False, True )
				
			elif(menu.lower() in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 Create an accompaniment
default                  Add default accompaniments
delete N                 delete the accompaniment with index N
d 0 1 2 3                delete each accompaniment listed (0 1 2 and 3)

h or help                Get some help
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving
m or main                Return to the main menu''')
				
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
				
			elif(menu.lower() in [ 'n', 'new' ] ):
				self.add(kind = 'accompaniment')
			elif(menu.lower() == 'default' ):
				for acc in [ 
							'Pasta',
							'Rice',
							'Potatoes',
							'Wheat',
							'Vegetable'
							]:
					if acc not in self.accompaniments:
						self.accompaniments.append(acc)
				
			elif menu.startswith('delete ') or menu.startswith('d ') :
				if menu.startswith('delete '):
					i = menu[7:].split(' ')
				else:
					i = menu[2:].split(' ')
				
				# get accompaniment index
				try:
					index = []
					for el in i:
						if el != '':
							index.append( int( el ) )
					
				except Exception as e:
					print('Error: «'+el+'» is not an integer')
					input('press enter to continue')
					continue
				
				# erase index duplicate values
				index = list( set( index ) )
				
				# check index is in the range
				error = False
				names = []
				for i in index:
					if i >= len(self.accompaniments) or i < 0:
						input('No accompaniment with index '+str(i)+'. press enter to continue.')
						error = True
						break
					else:
						names.append(self.accompaniments[i])
				if error:
					continue
				names = ', '.join(names)
				
				# ask to confirm
				if input('do you realy want to delete «'+names+'» accompaniments?(press enter to confirm or type anything to cancel)') != '':
					continue
				
				# erase each accompaniments
				index.sort(reverse=True)
				for i in index:
					self.accompaniments.pop(i)
	
	
	
	
	def manageRelatedMeal(self, main, path ):
		'''the menu to see and edit related meal list'''
		path = path.split('|')
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			maxPage = ceil(len(self.related) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.printSuggested( page )
			
			menu = input('your move ? (h for help):').strip()
			
			if(menu.lower() in ['exit', 'o', 'out', 'q', 'quit']):
				if( menu[0].isupper() ):
					return ( True, False, False )
				else:
					return ( False, False, False )
				
			elif(menu == 'SAFE'):
				return ( False, True, False )
				
			elif(menu.lower() in ['m', 'main']):
				return ( False, False, True )
				
			elif(menu.lower() in ['help', 'h']):
				print('''Help:

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
n or new                 Relate to another meal
d N or delete N          unrelate the meal with index N
d 0 1 2 3                unrelate each meal listed (0 1 2 and 3)

h or help                Get some help
q or quit                Quit the menu
Q or Quit                Quit the app (automatically save before)
SAFE                     Quit the app WITHOUT saving
m or main                Return to the main menu''')
				
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
				
			elif(menu.lower() in [ 'n', 'new' ] ):
				suggest = main.suggest( path[-1], main )
				
				if suggest is not None and suggest is not True:
					if( path != suggest and path not in self.related):
						self.related.append( suggest )
						
						path = '|'.join(path)
						suggest = main.getPath(suggest.split('|'))
						if path not in suggest.related:
							suggest.related.append( path )
				
			elif menu.startswith('delete ') or menu.startswith('d ') :
				if menu.startswith('delete '):
					i = menu[7:].split(' ')
				else:
					i = menu[2:].split(' ')
				
				# get related meal index
				try:
					index = []
					for el in i:
						if el != '':
							index.append( int( el ) )
					
				except Exception as e:
					print('Error: «'+el+'» is not an integer')
					input('press enter to continue')
					continue
				
				# erase index duplicate values
				index = list( set( index ) )
				
				# check index is in the range
				error = False
				names = []
				for i in index:
					if i >= len(self.related) or i < 0:
						input('No related meal with index '+str(i)+'. press enter to continue.')
						error = True
						break
					else:
						names.append(self.related[i].split('|')[-1])
				if error:
					continue
				names = ', '.join(names)
				
				# ask to confirm
				if input('do you realy want to delete «'+names+'» meal from the relate meal list?(press enter to confirm or type anything to cancel)') != '':
					continue
				
				# erase each ingredient
				index.sort(reverse=True)
				for i in index:
					relPath = self.related.pop(i).split('|')
					main.getPath(relPath).related.remove( '|'.join( path) )
			
	
	
	
	
	
	def printCoef(self, full = False , month = None ):
		'''display coefficients of the Element'''
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		
		if month is not None:
			month -= 1
			print('The coefficient is '+str( self.coef[ month ] )+' for '\
					+months[month]+'.')
		elif full:
			print('''The current coefficients, month by month, are:
January  => '''+str( self.coef[0] )+'''                July      => '''+str( self.coef[6] )+'''
February => '''+str( self.coef[1] )+'''                August    => '''+str( self.coef[7] )+'''
March    => '''+str( self.coef[2] )+'''                September => '''+str( self.coef[8] )+'''
April    => '''+str( self.coef[3] )+'''                October   => '''+str( self.coef[9] )+'''
May      => '''+str( self.coef[4] )+'''                November  => '''+str( self.coef[10] )+'''
June     => '''+str( self.coef[5] )+'''                December  => '''+str( self.coef[11] ))
		else:
			print('coefficients :'+str( self.coef ))
	
	
	
	
	def getPath(self, path):
		'''get element from path'''
		if len(path) > 0:
			s = path[0]
			
			for sub in self.sub:
				if sub.name == s:
					return sub.getPath( path[1:])
		else:
			return self
	
	
	
	
	
	def suggest(self, meal, main ):
		'''a method to suggest a meal to relate to another meal'''
		page = 0
		
		while(True):
			os.system('clear')# clear terminal output
			
			print('Suggest a meal to relate to «'+meal+'»:')
			
			maxPage = ceil(len(self.sub) / 15)-1
			if (page > maxPage):
				page = max ( 0, maxPage )
			
			self.print(page, main.month)
			
			if self.kind == 'variant':
				choice = input('Valid current choice (press enter)? (h for help):').strip()
			elif self.kind  == 'dish':
				choice = input('Valid this choice (ok) or specify a variant choice: (h for help):').strip()
			else:
				choice = input('your choice ? (h for help):').strip()
			
			if( choice.lower() in ['exit', 'o', 'out', 'q', 'quit'] ):
				return None
				
			elif( choice in ['c', 'cancel'] ):
				return True
				
			elif(choice in ['help', 'h']):
				print('''Suggest a related meal,Help:

suggest a meal that can be eaten in the same moment.

In menu:
Type:                    To:
< or -                   Previous 15 elements of the list
> or +                   Next 15 elements of the list
empty input              Same thing, back to first page when out of range
ok                       valid current selection, you only can suggest dishes group, dish or dish variant

c or cancel              Quit suggestion menu
q or quit                Go back to previous group
h or help                Get some help''')
				
				input('Press enter to continue')
			elif (choice == '' and self.kind == 'variant'):
				return self.name
			elif (choice.lower() == 'ok' 
						and self.kind in ['dish', 'variant'] ):
				return self.name
			elif ( choice in [ '-', '<' ] ):
				if page > 0:
					page -= 1
			elif (choice in [ '', '+', '>' ] ):
				maxPage = ceil(len(self.sub) / 15)
				
				if(page < maxPage):
					page += 1
				elif( choice == ''):
					page = 0
				else:
					page = maxPage
			else:
				try:
					choice = int(choice)
				except Exception as e:
					continue
				
				if choice < len( self.sub ):
					out = self.sub[choice].suggest( meal, main )
					if out is None:
						continue
					elif out is True:
						return True
					elif self.name!= 'Main':
						return self.name+'|'+out
					else:
						return out
		
		
	
	
	
	
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
	
	
	
	
	def printList(self, page, li = None, title = '' ):
		''' print part of the sub element list'''
		if li == None:
			li = self.sub
			if self.kind != 'dish':
				title = ''
		else:
			title = ' '+title
		
		# title
		print('		«'+self.name+'»'+title+' list:\n')
		
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
				if len(line) > 100:
					line = line[0:99] + '…'
				
			elif(type (li[i]) is tuple):
				if li[i][1] == '':
					line = li[i][0]
				else:
					line = li[i][1]+' of '+li[i][0]
				
			elif(type (li[i]) is str):
				line = li[i]
				
				# limit name size
				if len(line) > 100:
					line = line[0:99] + '…'
					
			
			# print name
			print(str(i)+'- '+line)
			i+=1
	
	
	
	
	def printSuggested( self, page):
		''' print part of the suggested meal list'''
		# title
		print('		«'+self.name+'» related meals list:\n')
		
		# empty list
		length = len(self.related)
		if length == 0:
			print('No suggested meals! type «n» to add one.')
			return
		
		# page limits
		i = page * 15
		end = i+15
		if end > length:
			end = length
		
		# print page list
		while(i < end):
			line = self.related[i].split('|')[-1]
			
			if len(line) > 100:
				line = line[0:99] + '…'
			
			
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
			
	

