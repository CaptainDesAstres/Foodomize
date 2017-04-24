#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''App main scope'''
from Element import Element
import xml.etree.ElementTree as xmlMod
import os

def main():
	'''app main function'''
	
	mainlist= Element()
	
	path = os.path.realpath(__file__+'/../foodList')
	if os.path.exists(path) and os.access( path, os.R_OK ):
		with open(path,'r') as backup:
			mainlist.load( xmlMod.fromstring( backup.read( ) ) )
			mainlist.editor = 'nano'
	else:
		mainlist.editor = 'nano'
	
	mainlist.menu()
	

main()
