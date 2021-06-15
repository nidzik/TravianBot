import urllib
from urllib.request import urlopen
from urllib.parse import urlencode, quote
from http.cookiejar import CookieJar, FileCookieJar,LWPCookieJar
import sys
import pymongo
import re
import requests, pickle, http
from html import unescape
#import thread_file
import time
import threading
from bs4 import BeautifulSoup
class Account():
	def __init__(self, username, *argv):
		self.user = username
		Account.argv = argv
		if self.user == 'beetchplz':
			self.dorf1 = 'https://ts4.travian.fr/dorf1.php'
			Account.dorf1 = self.dorf1
			Account.addr = 'https://ts4.travian.fr/'
		elif self.user == 'lebibot':
			self.dorf1 = 'https://tx10.mena.travian.com/dorf1.php'
			Account.dorf1 = self.dorf1
			Account.addr = 'https://tx10.mena.travian.com/'
		else:
			exit(1)	
		#self.cj =  FileCookieJar()
		try :
			self.cookie_file_LWP = 'cookie_file'
			self.cj = LWPCookieJar(self.cookie_file_LWP)
			if not self.cj:
				self.cj.load(self.cookie_file_LWP)
				print('Cookie set.')
		except : 
			print('error cookie')
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		Account.opener = self.opener
	def connect_db(self):
		myconnect = pymongo.MongoClient("mongodb://localhost:27017/")
		print(myconnect)
		Account.mydb = myconnect["travian-db"]
		Account.name_farm_db = 'farm_{}'.format(self.user)
	def init_user(self):
		print("__init_user:")
		users = self.mydb["users"]
		print(type(users))
		self.user_info = users.find_one({'username': self.user})
		self.password = self.user_info['password']
	
	def login(self):
		self.connect_db()
		self.init_user()
		self.connect_with_cookie()

	def connect_table(self, table_name):
		table = self.mydb[table_name]
		return table

	def check_connection_result(self):
		with open (self.file, 'r') as f:
			page = f.read().replace('\n', '')

		strings = re.findall(r'CONNEXION',page)
		captcha = re.findall(r'captcha', page)
		if ( strings == [] ):
			print('Successfully connect ')
			return 1
		else:
			print('Connection failed')
			if (captcha.count('captcha') > 0):
				print('get fucked by captcha')
				print(captcha)
			return 0

	def connect_with_cookie(self):
		if self.cj :
			print ('trying to log with cookie')
			#farm_page = self.opener.open('https://ts4.travian.fr/dorf1.php')
			farm_page = self.opener.open(self.dorf1)
			self.file = './dorf1.html'
			try :
				with open(self.file, 'w') as f:
					f.write(farm_page.read().decode('utf-8'))
			except IOError as e :
				print ('IOerro({0}): {1}'.format(e.errno, e.strerror))
			if self.check_connection_result():
				return
			else :
				self.connect_with_credentials()
		else :
			print('no cookies go to connect_with_credentials')
			self.connect_with_credentials()
	
	def connect_with_credentials(self):
		self.file = './connection.html'
		print('Trying login with credentials.')
		login_data = urlencode({'name' : self.user, 'password' : self.password, 's1': 'Se connecter', 'w': '1920:1080'})
		#print(login_data.encode('utf-8'))
		link = Account.addr + "/login.php?"
		connected = self.opener.open(link, login_data.encode('utf-8'))
		#print(connected.read().decode('utf-8'))
		with open(self.file, 'w') as f:
			f.write(connected.read().decode('utf-8'))
		if self.check_connection_result():
			self.cj.save()
			return
		else :
			print('Exiting : All login method tried had failed..')
			sys.exit(1)

class List(Account):
	def __init__(self):
		print('__init__ List')
		List.list_upgrade = []
		self.lvl_list = [1,2,3,4,5,6,7,8,9,10]
		self.farm_list = ['fer','terre','fer','cc','all']
		j = 0
		if len(sys.argv) > 2:
			for i in Account.argv[0]:
				if j >= 2:
					List.list_upgrade.append(i)
				j = j +1
			print(List.list_upgrade)
	def check_entry(self, user_input):
		arr = user_input.split()
		farm = None
		lvl = None
		tmp = -1
		#for i in user_input_array:
		if arr and arr[1] and arr[1] in self.farm_list:
			farm = arr[1]
			if len(arr) > 1 and arr[2]:
				try:
					tmp = int(arr[2])
				except:
					print('error in parsing lvl')
			else:
				print('not enought args')
			if tmp in self.lvl_list:
				lvl = tmp
		else:
			print('error in farm parsing ')
			return
		print('Farm : {}  Lvl : {}'.format(farm, lvl)) 
		if farm and lvl:
			self.add_entry(user_input)
		else:
			print('error in parsing user entry ')
			unser_entry = None

	def handle_entry(self, user_input):
		self.check_entry(user_input)

	def add_entry(self, user_input):
		List.list_upgrade.append(user_input)
		print('new entry is : {}, list entry is : {}'.format( user_input, List.list_upgrade))
	def check_user_list(self, user_input):
		print(user_input)
		if len(sys.argv) > 2 or user_input:
			for i in List.list_upgrade:
				print('check{}'.format(i))
				if i in self.farm_list:
					farm = i
					print('found farm : ok ')
				elif int(i) in self.lvl_list:
					lvl = i
					print('found lvl : ok')
				else : 
					print('error in user entry')
					return
		return {'farm':farm, 'lvl' : lvl}
class Village(List):
	def __init__(self):
		pass

	def check_number(self):
		with open ('./dorf1.html', 'r') as f:
			page = BeautifulSoup(f.read().replace('\n', ''), 'html.parser')
		matches = re.finditer(r'class=\"slots\">.*?(\d|\d\d).*?span', str(page))
		if not matches :
			print('parsing village failed returning ')
			return -1
		for matchNum, match in enumerate(matches, start=1):
			for groupNum in range(0, len(match.groups())):
				groupNum = groupNum + 1
				nb_village = int(match.group(groupNum))
				return nb_village

	def get_list_url(self):
		list_url_village = []
		with open ('./dorf1.html', 'r') as f:
			page = BeautifulSoup(f.read().replace('\n', ''), 'html.parser')
		matches = re.finditer(r'\?newdid=\d{3,6}&', str(page))
		if not matches :
			print('parsing village failed returning ')
			return -1
		for matchNum, match in enumerate(matches, start=1):
			if matchNum != 1:
				list_url_village.append(match.group())
		return list_url_village
	
class Farm(Village):
	def __init__(self):
		print('__init__ Farm')
		self.farms = Account.connect_table(self, Account.name_farm_db)
		self.addr = Account.addr
		self.opener = Account.opener

	def parse_farm(self, id_village):
		print("{}{}",id_village, self.get_list_url)
		tmp_url_village = self.get_list_url()
		url_village  = tmp_url_village[id_village ]
		link_village = "{}{}".format(Account.dorf1,  url_village)
		self.request('./dorf1.html', link_village  , Account.dorf1)
		with open ('./dorf1.html', 'r') as f:
			page = f.read().replace('\n', '')
		matches = re.finditer(r'class=\"( |notNow |good )level.*?colorLayer.*?level..', page)
		'''
		for matchNum, match in enumerate(matches, start=1):
			print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
		for groupNum in range(0, len(match.groups())):
			groupNum = groupNum + 1
			print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
'''
		list_farm = []
		i = 1
		for matchNum, match in enumerate(matches, start=1):
			clean_line  = match.group(0)[7:].strip()
			#print(clean_line)
			status = re.match(r'^.*?level',clean_line)
			status = status.group(0)
			if status == 'level':
				status = 'bad'
			#print(status)
			type_farm = re.search(r'gid.', clean_line).group(0)
			type_gid = {'gid1': 'bois', 'gid2': 'terre', 'gid3': 'fer', 'gid4': 'cc' }
			farm_type = type_gid[type_farm]
			level = int(re.search(r'level\d(\d|)', clean_line).group(0).replace('level', ''))
			farm_id = int(re.search(r'buildingSlot\d(\d|)', clean_line).group(0).replace('buildingSlot', ''))
			link_farm = 'build.php?id={}'.format(farm_id)
			list_farm.append({ 'id_farm' : farm_id, 'type' : farm_type, 'level' : level, 'status' : status, 'link_farm' : link_farm, 'evol' : level, 'id_village' : id_village})
		return list_farm

	def parse_construct(self):	
		contruct_list = [{None}]
		with open ('./dorf1.html', 'r') as f:
			page = f.read().replace('\n', '')
		matches = re.finditer(r'Centre du village</title.*?li>.*?ul>', page)
		for matchNum, match in enumerate(matches, start=1):
			print(match.group())
			glob_match = match.group()
		matches = re.finditer(r'class=\"name\">(.*?)<span.*?lvl\">(Niveau \d{1,2})</span', glob_match)

		for matchNum, match in enumerate(matches, start=1):
			print ("{} Match {matchNum} was found at {start}-{end}: {match}".format(len(match.groups()), matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
			for groupNum in range(0, len(match.groups())):
				groupNum = groupNum + 1
				
				print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
					

	def print_table(self, tablename):
			
		table = Account.mydb[tablename]
		for j in table.find():
			print(j)
	
	def retfarm(self):
		return Account.mydb[Account.name_farm_db] 

	def create_farm_db(self, list_farm):
		#farms = Account.mydb["farm"]
		farms = self.farms
		try : 
			farms.insert_many(list_farm)
		except :
			print('Duplicate id key, cannot insert value.') 
			return -1 
		print('All entry inserted')	

	def update_farm_reset(self,list_farm):
		counter= 0 
		for i in list_farm:
			tmp = self.farms.replace_one({"id_farm" : i['id_farm'], "id_village" : i["id_village"]}, i )
			counter = counter +   tmp.modified_count
		if counter == 0 :
			self.create_farm_db(list_farm)
	def update_farm(self,list_farm):
		print("__update_farm()")
		counter= 0 
		for i in list_farm:
			query = self.farms.find_one({ 'evol':{"$gt": i['level']}, "id_farm" : i['id_farm'], "id_village" : i["id_village"]})
			if query:
				print("{} is in construction".format(query))
			if query is None:
				tmp = self.farms.replace_one({"id_farm" : i['id_farm'], "id_village" : i["id_village"]}, i )
				counter = counter +   tmp.modified_count
			else:
				#print("conflict found : lvl query :{} {}  lvl list :{} {} ".format(query['level'], type(query['level']), i['level'], type(i['level']) ))
				if query and query['level'] != i['level']:
					tmp = self.farms.replace_one({"id_farm" : i['id_farm'], "id_village" : i["id_village"]}, i )
					counter = counter +   tmp.modified_count
		if not counter:
			print('nothing to update')
		else:
			print("{} entry updated in farm".format(counter))
		
	def request(self, file, link, referer):
		header = urlencode([('Host', 'ts4.travian.fr'),
			('Referer', 'https://ts4.travian.fr/build.php?id=4'),
			('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'),
			('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
			('Accept-Language', 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'),
			('Accept-Encoding','gzip, deflate, br'),
			('Connection', 'keep-alive'),
			('Referer', referer),
			('Upgrade-Insecure-Requests', '1'),
			('TE', 'Trailers')
			])
		self.opener.addheader = header.encode('utf-8')
		req = self.opener.open(link)
		with open(file, 'w') as f:
			f.write(req.read().decode('utf-8'))

	def lvl_up_all(self, levell, village):
		id_village = village 
		level = int(levell)
		print("lvlupall..")
		query = self.farms.find_one({'level':{"$lt": level}, 'status' : {"$regex": "^good"}, 'evol' : {"$lt": level}, 'id_village' : id_village})
		if query:
			print("{} lvl {} en construction".format(query['type'], query['level']))
		if not query:
			ll = int(level)	
			queryy = self.farms.find_one({'level' : { "$lt" : ll}, 'id_village' : id_village})
			if queryy is None :
				print("all farms are lvl {}, deleting elem".format(level))
				return -1 
			return 0
		print(query)
		#for i in query:
		#	print("- {} {} -".format(i['type'] , i['level']))

		formated_addr = "{}{}".format(self.addr, query['link_farm'])
		farm_update = self.opener.open(formated_addr)
		self.file = 'update_farm.html'
		with open(self.file, 'w') as f:
			f.write(farm_update.read().decode('utf8'))
		addr_args = self.parse_lvl_up(self.file)
		if not addr_args:
			return ; 
		link_update = self.addr +'dorf1.php?'+ addr_args
		#dorf = self.opener.open(link_update)
		query['evol']  = query['level'] + 1 
		tmp = self.farms.replace_one({"id_farm" : query['id_farm'], 'id_village' : id_village}, query )
		counter = tmp.modified_count
		if not counter:
			print('nothing to update')
		else:
			print("{} entry updated in farm".format(counter))
		self.request('dorf1.html', link_update, formated_addr)

	def lvl_up(self, farm_type, level):
		print('lvl_up()  vv result_query vv')
		query = self.farms.find_one({'type':farm_type})
		print(query)
		if query and query['level'] >= int(level):
			print('all farm already at this lvl, deleting elem in list')
			return -1
		formated_addr = "{}{}".format(self.addr, query['link_farm'])
		farm_update = self.opener.open(formated_addr)
		self.file = 'update_farm.html'
		with open(self.file, 'w') as f:
			f.write(farm_update.read().decode('utf8'))
		addr_args = self.parse_lvl_up(self.file)
		if not addr_args:
			return ; 
		link_update = self.addr +'dorf1.php?'+ addr_args
		#dorf = self.opener.open(link_update)
		print(link_update)
		self.request('dorf1.html', link_update, formated_addr)

	def parse_lvl_up(self, file):
		print('parse_lvl_up()')
		clean_line = None
		with open (file, 'r') as f:
			page = f.read().replace('\n', '')
		matches = re.finditer(r"<but(.*?)niveau(.*?)dorf1\.php\?(.*?)';(.*?)Button", page)
		## CAREFULL CAN USE GOLD 
		for matchNum, match in enumerate(matches, start=1):
			clean_line  = unescape(match.group(3))#[7:].strip()
			break
		if clean_line and ('b=') in clean_line:
			print("GOLD WILL BE SPEND, CANCEL..")
			clean_line = None
		return clean_line

class Checker(Farm):
	def __init__(self):
		print('coucou')
		print('__init__ Checker')
		#self.farms = Farm.farms
		self.farms = self.retfarm()

	def is_spe_upgrade_avalible(self,farm_type, lvl):
		#self.print_table('Farm')
		query = self.farms.find({'status' : 'good level', 'type': farm_type, 'level': lvl})
		if not query:
			print('No upgrae avalible')
			return 0
		else: 
			print('upgrade {} lvl {} avalible'.format(farm_type, lvl))
			return 1

	def is_upgrade_avalible(self):
		query = self.farms.find({'status' : 'good level'})
		for i in query:	
			if not i:
				print ("KO")
			print(i)
		if not query:
			print('No upgrae avalible')
			return 0
		else: 
			print('upgrade avalible')
			return 1

	def check_elem_list(self, list_upgrade):
		if self.is_upgrade_avalible() == 0 :
			print('0 upgrade avalible, cancel checker') 
			return
		else :
			print("got fucked")
		k =0
		for i in list_upgrade:
			j = i.split()
			print('{} {}'.format(i, j))
			if k == 0 or j[-1] == '-':
				if j[0][0] == 'v':
					vivi = re.findall(r'\d+',j[0])
					self.update_farm(self.parse_farm(int(vivi[0])))
					if j[1] == 'all':
						if self.lvl_up_all(j[2],int(vivi[0])) == -1 :
							del list_upgrade[0]
			k = k+1

		'''arr = list_upgrade[0].split()
		if arr[0] == 'del':
			print("Deleting list")
			list_upgrade = []
			return
		if arr[0][0] == 'v':
			print ('okokok')
			print(arr[0])
			vivi = re.findall(r'\d+',arr[0])
			print(vivi[0]) 
			self.update_farm(self.parse_farm(int(vivi[0])))
			if arr[1] == 'all':
				if self.lvl_up_all(arr[2],int(vivi[0])) == -1 :
					del list_upgrade[0]
		else: 
			print("KO VVVV")'''
		return
		for i in list_upgrade:
			if self.is_spe_upgrade_avalible(arr[0], arr[1]) == 1:
				if self.lvl_up(arr[0], arr[1]) == -1:
					del list_upgrade[0]

	def check_list(self):
		if not List.list_upgrade or List.list_upgrade == []:
			print('nothing in the upgrade list.. waiting.. or exiting.. dkdc.--{}--'.format(List.list_upgrade))
		else :
			print('list_upgrade : {}'.format(List.list_upgrade))
			self.check_elem_list(List.list_upgrade)
			
class Hoo(Checker):
	def ok(self):
		print(List.list_upgrade)

class MyThreadCheck(Checker):
	#def __init(self):
	#	print('__init__ ThreadCheck')
	def background(self):
		print('in bckground')
		while True:
			self.check_list()
			time.sleep(60)
	def loop(self):
		print('entering loop')
		# now threading1 runs regardless of user input
		threading1 = threading.Thread(target=self.background)
		threading1.daemon = True
		threading1.start()
		print('bckground complete')
	#	while True:
	#		time.sleep(1)#print(List.list_upgrade)
	#def print_list():
		#print(List.list_upgrade)

class MyThread(List):
	def __init__(self, List):
		print('__init__ Mythread')
		print(self.list_upgrade)
		self.farm_list = List.farm_list
		self.lvl_list = List.lvl_list
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
				#self.check_list()
				self.ui = None

"""
username = 'AwsomeUSer'
password = 'AwsomePsswd'
resp1 = opener.open('https://ts4.travian.fr/login.php?name=AwsomeUser&password=AwsomePsswd&s1=Se+connecter&w=1920%3A1080')
resp = opener.open('https://ts4.travian.fr/login.php', login_data)
farmv3 = opener.open('https://ts4.travian.fr/dorf1.php?newdid=20009&')
with open('/tmp/farm.html', 'a') as f:
	f.write(farmv3.read())
#slot8 = opener.open('https://ts4.travian.fr/build.php?id=8')
#construct = opener.open('https://ts4.travian.fr/dorf1.php?a=8&c=e5c629')
#with open('/tmp/result.html', 'a') as f:
#	f.write(construct.read())
"""

if __name__ == '__main__':
	username = sys.argv[1]
	account = Account(username, sys.argv)
	account.login()
	l = List()
	vivi = Village()
	farm = Farm()
	#l.check_user_list()
	#farm.create_farm_db(farm.parse_farm())
	#for i in range(0, vivi.check_number()):
		#farm.update_farm_reset(farm.parse_farm(i))
	#farm.parse_construct()
	#farm.lvl_up('fer', 2)
	#farm.parse_lvl_up('update_farm.html')
	

	#print (List.list_upgrade)

	#Hoo().ok()
	#Checker()
	op = MyThreadCheck()
	print('after instancification' )
	op.loop()
	gg = MyThread(l)
	gg.loop()
	print('hello')

'''	def background(self):
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
