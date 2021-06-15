import re
from bs4 import BeautifulSoup
import pymongo

class Village():
	def check_number(self):
		with open ('./dorf1.html', 'r') as f:
			 page = BeautifulSoup(f.read().replace('\n', ''), 'html.parser')
		matches = re.finditer(r'class=\"slots\">.*?(\d|\d\d).*?span', str(page))
		#print(matches.group(0))
		if not matches :
			print('parsing village failed returning ')
			return -1
		for matchNum, match in enumerate(matches, start=1):
			for groupNum in range(0, len(match.groups())):
				groupNum = groupNum + 1
				nb_village = int(match.group(groupNum))
				return nb_village


	def get_list_url(self):	
		print('okok')
		list_url_village = []
		with open ('./dorf1.html', 'r') as f:
			 page = BeautifulSoup(f.read().replace('\n', ''), 'html.parser')
		matches = re.finditer(r'\?newdid=\d{3,6}&', str(page))
		if not matches :
			print('parsing village failed returning ')
			return -1
		for matchNum, match in enumerate(matches, start=1):
			print(match.group())
			if matchNum != 1:
				list_url_village.append(match.group())	
		return list_url_village



	def check_village_db(self):
		myconnect = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myconnect['travian-db']
		users.find
		
if __name__ == '__main__':
	dd = Village()
	print(dd.check_number())
	print(dd.get_list_url())
