import threading
import time
import sys
from account import List, Checker
from getch import getch

class MyThread(List):
	#def __init__(self):
	#	print('__init__ Mythread')
		#print(self.list_upgrade)
	ui = ""
	def background(self):
		while True:
			time.sleep(1)
			self.ui = input()

	def loop(self):	
		# now threading1 runs regardless of user input
		threading1 = threading.Thread(target=self.background)
		threading1.daemon = True
		threading1.start()
		
		while True:
			if self.ui == 'exit':
 				#other_function()
				sys.exit()
			elif self.ui :
				#print("input is : {}.".format(self.ui))
				self.handle_entry(self.ui)
				self.ui = None


'''class MyThreadCheck(Checker):
	def background(self):
		while True:
			time.sleep(5)
	def loop(self):
		# now threading1 runs regardless of user input
		threading1 = threading.Thread(target=self.background)
		threading1.daemon = True
		threading1.start()

		while True:
			print(List.list_upgrade)
		
		#self.check_list()'''
