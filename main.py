#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''App main scope'''


def main():
	'''app main function'''
	
	while(True):
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
