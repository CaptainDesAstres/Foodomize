#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''App main scope'''
import os
from Element import Element

def main():
	'''app main function'''
	
	mainlist= Element()
	
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
	
	
	
	
	
	
	
	

main()
