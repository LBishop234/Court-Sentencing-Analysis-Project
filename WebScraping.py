import time, selenium, re, datetime, threading, _thread
#import requests, sqlite3
import urllib.request as urllib2
import sqlalchemy as db
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from contextlib import contextmanager

UserName = "LMBishop"
Password = "Canford2014B"
#inclusive
CalStartDay = 1
CalStartMonth = "January"
CalStartYear = 2018
#exclusive
CalEndDay = 1
CalEndMonth = "January"
CalEndYear = 2019

class CalendarDate:
	day = 0
	month = 'Hold'
	year = 0

	def __init__(self, d, m, y):
		self.day = int(d)
		self.month = str(m)
		self.year = int(y)

	def Set_Date(self, d, m, y):
		self.day = int(d)
		self.month = str(m)
		self.year = int(y)

	def Next_Month(self):
		if self.month == 'January':
			self.month = 'February'
		elif self.month == 'February':
			self.month = 'March'
		elif self.month == 'March':
			self.month = 'April'
		elif self.month == 'April':
			self.month = 'May'
		elif self.month == 'May':
			self.month = 'June'
		elif self.month == 'June':
			self.month = 'July'
		elif self.month == 'July':
			self.month = 'August'
		elif self.month == 'August':
			self.month = 'September'
		elif self.month == 'September':
			self.month = 'October'
		elif self.month == 'October':
			self.month = 'November'
		elif self.month == 'November':
			self.month = 'December'
		elif self.month == 'December':
			self.month = 'January'
			self.Next_Year()

	def Next_Year(self):
		#blah
		self.year = self.year + 1

	def Next_Day(self):
		if self.day == 28 and self.month == 'February':
			self.day = 1
			self.Next_Month()
		elif self.day == 30 and (self.month == 'April' or self.month == 'June' or self.month == 'September' or self.month == 'November'):
			self.day = 1
			self.Next_Month()
		elif self.day == 31:
			self.day = 1
			self.Next_Month()
		else:
			self.day = self.day + 1


class TimeoutException(Exception):
	def __init__(self, msg=''):
		self.msg = msg

@contextmanager
def timeLimit(seconds, msg=''):
	timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
	timer.start()
	try:
		yield
	#except KeyboardInterrupt:
	except:
		raise TimeoutException("Operation timed out: {}".format(msg))
	finally:
		timer.cancel()

def AcceptCookies(driver):
	#clicks on (therefore removing) the cookies popup
	popupButton = driver.find_element_by_id("submitButtons")
	driver.implicitly_wait(2)
	popupButton.click()

def Login(driver):
	#selects neccessery elements
	driver.get("https://www.thelawpages.com/login.php")
	userName = driver.find_element_by_id("user")
	password = driver.find_element_by_id("pass")
	remeberMe = driver.find_element_by_xpath("/html/body/div[7]/div[10]/table[1]/tbody/tr[2]/td/form/table/tbody/tr/td/center/div/div/div/div/div/table/tbody/tr[4]/td[3]/input")
	login = driver.find_element_by_id("submitButton")

	AcceptCookies(driver)

	#fills in values and logs in
	userName.send_keys(UserName)
	password.send_keys(Password)
	remeberMe.click()
	login.click()

	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("paneContent0"))

def FillSearchFields(driver, targetDate):
	#return messages: 1=ok, 2=weekend day, -1=invalid
	foundFlag = False
	#loads the search page and waits till the page is loaded
	driver.get("https://www.thelawpages.com/court-cases/court-case-search.php?mode=3")
	assert len(driver.window_handles) == 1
	WebDriverWait(driver, 10).until(EC.title_is("Crown Court Cases Results Criminal Sentences Crime Offence Judge Solicitor Barrister"))

	targetMonthYear = targetDate.month + ', ' + str(targetDate.year)

	#finds the calendar and court type elements
	cal1 = driver.find_element_by_id("cal1")
	cal2 = driver.find_element_by_id("cal12")
	courtType = driver.find_element_by_id("c_type")

	#fills the dates
	cal1.click()
	currentSelected1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
	backMonth1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
	while currentSelected1.text != targetMonthYear:
		backMonth1.click()
	dayParentElement = driver.find_element_by_xpath('/html/body/div[8]/table/tbody')
	dayElements = dayParentElement.find_elements_by_class_name('day.false')
	weekendElements = dayParentElement.find_elements_by_class_name('day.false.weekend')
	for count in range(len(dayElements)):
		if dayElements[count].text == str(targetDate.day):
			dayElements[count].click()
			foundFlag = True
			break
	if foundFlag == False:
		for count in range(len(weekendElements)):
			if weekendElements[count].text == str(targetDate.day):
				return 2
		return -1

	foundFlag = False
	cal2.click()
	currentSelected2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
	backMonth2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
	while currentSelected2.text != targetMonthYear:
		backMonth2.click()
	dayParentElement = driver.find_element_by_xpath('/html/body/div[8]/table/tbody')
	dayElements = dayParentElement.find_elements_by_class_name('day.false')
	weekendElements = dayParentElement.find_elements_by_class_name('day.false.weekend')
	for count in range(len(dayElements)):
		if dayElements[count].text == str(targetDate.day):
			dayElements[count].click()
			foundFlag = True
			break
	if foundFlag == False:
		for count in range(len(weekendElements)):
			if weekendElements[count].text == str(targetDate.day):
				return 2
		return -1

	#selects the court type and court location 
	courtType.send_keys("Crown Court")
	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("court_location"))
	#selects the searcg button and clicks it
	searchButton = driver.find_element_by_id("submitButton")
	searchButton.click()

	#waits until the results are loaded
	try:
		WebDriverWait(driver, 5).until(lambda d: d.find_element_by_id("myTable"))
	except:
		return 2
	return 1

def LoadEntryPage(driver):
	html = driver.page_source
	soup = BeautifulSoup(html, features="lxml")

	holdElements = soup.find_all("tbody")
	tableElements = holdElements[3:23]

	#finding the ID of the current Line
	count = 0
	flag = False
	while flag == False:
		try:
			IDLine = re.search(r'onclick="tbllink\(\S*\)', str(tableElements[count]))
			ID = re.search(r'\(\S*\)', IDLine.group()).group()
			ID = ID[2:len(ID)-6]
			flag = CheckID(ID)
			count = count + 1
		except:
			return -1
	#clicks on the selected entry
	tableEntryLink = driver.find_element_by_xpath("/html/body/div[7]/div[9]/table[1]/tbody/tr[1]/td/table/tbody/tr/td/center/div/table[2]/tbody[" + str(count) + "]/tr")
	tableEntryLink.click()
	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("maincontent"))
	return ID

def CheckID(ID):
	#checks if the passed ID already is held in the database
	query = db.select([records]).where(records.columns.ID == ID)
	resultProxy = connection.execute(query)
	results = resultProxy.fetchall()
	if len(results) < 1:
		return True
	else:
		return False

def ScrapeEntry(driver):
	html = driver.page_source
	soup = BeautifulSoup(html, features="lxml")

	tableData = soup.find("table")
	tableDataList = tableData.find_all("td")
	#fetches all text elements from the HTML file
	textList = []
	for element in tableDataList:
		try:
			thisText = element.get_text()
			textList.append(thisText)
		except:
			flag = True
	#strips whitespace and HTML commands from the text
	holdList = []
	strippedList = []
	for x in range(len(textList)):
		textList[x] = textList[x].replace('\n', '')
		if textList[x] != '\xa0':
			holdList.append(textList[x])
	for x in range(len(holdList)):
		holdList[x] = holdList[x].replace('\xa0', '')
		holdList[x] = holdList[x].replace('\t', '')
		if holdList[x] != ':':
			strippedList.append(holdList[x])
	count = 0
	while count < len(strippedList):
		#if strippedList[count].find(':') != -1:
		if strippedList[count] == (':'):
			del strippedList[count]
		else:
			count = count + 1
	#confirm strips whitespace from data entries
	for x in range(len(strippedList)):
		strippedList[x] = strippedList[x].strip()
	return strippedList

def ExtractValuesFromData(dataList, ID):
	count = 0
	flag = False
	data = [None] * 23
	charges = []
	sentances = []
	#disgusting if statement selecting the column values from the text list
	data[0] = ID
	while count < len(dataList):
		if dataList[count] == 'Country':
			data[1] = dataList[count + 1]
		elif dataList[count] == 'Date':
			data[2] = dataList[count + 1]
		elif dataList[count] == 'Court':
			data[3] = dataList[count + 1]
		elif dataList[count] == 'Judge':
			data[4] = dataList[count + 1]
		elif dataList[count] == 'Case number':
			data[5] = dataList[count + 1]
		elif dataList[count] == 'Name':
			data[6] = dataList[count + 1]
		elif dataList[count] == 'Gender':
			data[7] = dataList[count + 1]
		elif dataList[count] == 'Age':
			data[8] = dataList[count + 1]
		elif dataList[count] == 'Co-Defendant/s':
			data[9] = dataList[count + 1]
		elif dataList[count] == 'Bail Position':
			data[10] = dataList[count + 1]
		elif dataList[count] == 'Offence':
			charges.append(dataList[count + 1])
		elif dataList[count] == 'Sentence':
			sentances.append(dataList[count + 1])
		elif dataList[count] == 'Order':
			data[13] = dataList[count + 2]
		elif dataList[count] == 'Sentencing Considerations':
			data[14] = dataList[count + 1]
		elif dataList[count] == 'Public Protection Sentence':
			data[15] = dataList[count + 1]
		elif dataList[count] == 'Total Sentence':
			flag = True
			data[16] = dataList[count + 1]
		elif dataList[count] == 'Parole Eligibility Date (PED)' or dataList[count] == 'Likely Release / Eligibility Date':
			data[17] = dataList[count + 1]
		elif dataList[count] == 'Mitigating & Aggravating Factors':
			data[18] = dataList[count + 1]
		elif dataList[count] == 'Sentenced':
			flag = True
			data[19] = dataList[count + 1]
		elif dataList[count] == 'Prosecuting Authority':
			flag = True
			data[20] = dataList[count + 1]
		elif dataList[count] == 'Police Area':
			flag = True
			data[21] = dataList[count + 1]
		#extra code to select the multiple possible charges/sentances
		if flag == True:
			strippedCharges = []
			strippedSentances = []
			for element in charges:
				if element != None:
					strippedCharges.append(element)
			for element in sentances:
				if element != None:
					strippedSentances.append(element)
			data[11] = strippedCharges
			data[12] = strippedSentances
		count = count + 1
	return data

def ConvertToDate(preDate):
	#converts a date string to a date data type
	try:
		if str(preDate).find('-') != -1:
			dateList = preDate.split('-')
		elif str(preDate).find('/') != -1:
			dateList = preDate.split('/')
		flag = False
		if dateList[0] == '0':
			dateList[0] = '1'
		if dateList[1] == '0':
			dateList[1] = '1'
		if dateList[2] == '0':
			dataList[2] = '1'
		while flag == False:
			try:
				date = datetime.date(int(dateList[2]), int(dateList[1]), int(dateList[0]))
				flag = True
			except:	
				dateList[0] = str(int(dateList[0]) - 1)
		return date
	except:
		return None

def CheckingForTable(engine):
	#checks if the record table exists
	tables = engine.table_names()
	if 'CourtRecords' in tables:
		return True
	else:
		return False

def CreateTable():
	records = db.Table('records', metadata, 
		db.Column('ID', db.String, primary_key = True),
		db.Column('CaseNumber', db.String),
		db.Column('Date', db.Date),
		db.Column('Name', db.String),
		db.Column('Country', db.String),
		db.Column('Court', db.String),
		db.Column('Judge', db.String),
		db.Column('Gender', db.String),
		db.Column('Age', db.Integer),
		db.Column('CoDefendants', db.String),
		db.Column('BailPosition', db.String),
		db.Column('Charges', db.String),
		db.Column('Sentances', db.String),
		db.Column('Order', db.String),
		db.Column('PublicProtectionSentence', db.String),
		db.Column('SentencingConsiderations', db.String),
		db.Column('MitigatingAndAggravatingFactors', db.String),
		#db.Column('DefendantHasSimilarPreviousConvictions', db.String),
		db.Column('Sentenced', db.String),
		db.Column('TotalSentence', db.String),
		db.Column('EarliestReleaseDate', db.Date),
		db.Column('ProsecutingAuthority', db.String),
		db.Column('PoliceArea', db.String)
	)
	metadata.create_all(engine)
	return records

def PassInEntry(records, entryData):
	string_token = ','
	try:
		holdAge = int(entryData[8])
	except:
		holdAge = None
	try:
		with timeLimit(10, 'pass in records'):
			if entryData[5] == None:
				query = db.insert(records).values(ID=str(entryData[0]))
			else:	
				query = db.insert(records).values(ID=str(entryData[0]), CaseNumber=str(entryData[5]), Date=ConvertToDate(entryData[2]), Name=str(entryData[6]), Country=str(entryData[1]), Court=str(entryData[3]), Judge=str(entryData[4]), Gender=str(entryData[7]), Age=holdAge, CoDefendants=str(entryData[9]), BailPosition=str(entryData[10]), Charges=str(string_token.join(entryData[11])), Sentances=str(string_token.join(entryData[12])), Order=str(entryData[13]), PublicProtectionSentence=str(entryData[15]), SentencingConsiderations=str(entryData[14]), MitigatingAndAggravatingFactors=str(entryData[18]), Sentenced=str(entryData[19]), TotalSentence=str(entryData[16]), EarliestReleaseDate=ConvertToDate(entryData[17]) , ProsecutingAuthority=str(entryData[20]), PoliceArea=str(entryData[21]))
			commit = engine.execute(query)
	except:
		pass

def CheckForCaptcha(driver):
	try:
		findCaptcha = driver.find_element_by_id('captcha')
		return True
	except:
		return False

def mainloop(driver):
	searchAttempt = FillSearchFields(driver, currentDate)
	if searchAttempt == 2:
		currentDate.Next_Day()
		return 2
	elif searchAttempt == -1:
		print('INVALID DAY!')
		return -1
	elif searchAttempt == 1:
		driver.implicitly_wait(1)
		entryID = LoadEntryPage(driver)
		captchaCheck = CheckForCaptcha(driver)
		if captchaCheck == True:
			captchaCheck = False
			return 1
		elif entryID == -1:
			currentDate.Next_Day()
			return 2
		else:
			scrapedEntryData = ScrapeEntry(driver)
			valuesEntryData = ExtractValuesFromData(scrapedEntryData, entryID)
			PassInEntry(records, valuesEntryData)
			print(valuesEntryData)
		return 0
			

startTime = datetime.datetime.now()
print('Start Time: ' + str(startTime))

#sets up the table
engine = db.create_engine('sqlite:///SQLite-Main-Database.db')
connection = engine.connect()
metadata = db.MetaData()
foundTable = CheckingForTable(engine)
if foundTable == False:
	records = CreateTable()
else:
	records = db.Table('records', metadata, autoload=True, autoload_with=engine)

Chrome(executable_path='C:/WebDriver/bin/chromedriver')
driver = Chrome()
Login(driver)

entryCount = 0
exceptionCount = 0
currentDate = CalendarDate(CalStartDay, CalStartMonth, CalStartYear)
while currentDate.day != CalEndDay or currentDate.month != CalEndMonth or currentDate.year != CalEndYear:
	try:
		with timeLimit(30, 'sleep'):
			loopStatus = mainloop(driver)
			if loopStatus == -1:
				break
			elif loopStatus == 1:
				driver.quit()
				driver = Chrome()
				driver.implicitly_wait(1)
				Login(driver)
			elif loopStatus == 0:
				entryCount = entryCount + 1
				print('count: ' + str(entryCount))
				print('')
		exceptionCount = 0
	except Exception as e:
		print('Exception Thrown')
		print(e)
		exceptionCount = exceptionCount + 1
		if exceptionCount < 3:
			pass
		else:
			break

print('Finished Scrape!')
endTime = datetime.datetime.now()
elapsedTime = endTime - startTime
print('End Time: ' + str(endTime))
print('Elapsed Time: ' + str(elapsedTime))
driver.quit()