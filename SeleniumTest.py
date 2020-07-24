import time, selenium, requests, re, sqlite3, datetime
import urllib.request as urllib2
import sqlalchemy as db
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome

UserName = "LMBishop"
Password = "Canford2014B"
CalStartMonth = "May, 2019"
CalEndMonth = "May, 2020"
EndDate = '06/2020'

def AcceptCookies():
	#clicks on (therefore removing) the cookies popup
	popupButton = driver.find_element_by_id("submitButtons")
	driver.implicitly_wait(2)
	popupButton.click()

def Login():
	#selects neccessery elements
	driver.get("https://www.thelawpages.com/login.php")
	userName = driver.find_element_by_id("user")
	password = driver.find_element_by_id("pass")
	remeberMe = driver.find_element_by_xpath("/html/body/div[7]/div[10]/table[1]/tbody/tr[2]/td/form/table/tbody/tr/td/center/div/div/div/div/div/table/tbody/tr[4]/td[3]/input")
	login = driver.find_element_by_id("submitButton")

	AcceptCookies()

	#fills in values and logs in
	userName.send_keys(UserName)
	password.send_keys(Password)
	remeberMe.click()
	login.click()

	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("paneContent0"))

def FillSearchFields():
	#loads the search page and waits till the page is loaded
	driver.get("https://www.thelawpages.com/court-cases/court-case-search.php?mode=3")
	assert len(driver.window_handles) == 1
	WebDriverWait(driver, 10).until(EC.title_is("Crown Court Cases Results Criminal Sentences Crime Offence Judge Solicitor Barrister"))

	#finds the first three
	cal1 = driver.find_element_by_id("cal1")
	cal2 = driver.find_element_by_id("cal12")
	courtType = driver.find_element_by_id("c_type")

	#fills in the first date
	cal1.click()
	currentSelected1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
	backYear1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[1]")
	backMonth1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
	backYear1.click()
	while(currentSelected1.text != CalStartMonth):
		backMonth1.click()
	selectDay1 = driver.find_element_by_xpath("/html/body/div[7]/div[9]/table/tbody/tr/td/form/table/tbody/tr[1]/td/div/div/table/tbody/tr[4]/td[3]")
	selectDay1.click()

	#fills in the second date
	cal2.click()
	currentSelected2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
	backMonth2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
	while(currentSelected2.text != CalEndMonth):
		backMonth2.click()
	selectDay2 = driver.find_element_by_xpath("/html/body/div[7]/div[9]/table/tbody/tr/td/form/table/tbody/tr[1]/td/div/div/table/tbody/tr[11]/td[3]/label/input")
	selectDay2.click()

	#selects the court type and court location 
	courtType.send_keys("Crown Court")
	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("court_location"))
	#selects the searcg button and clicks it
	searchButton = driver.find_element_by_id("submitButton")
	searchButton.click()

	#waits until the results are loaded
	WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("myTable"))

def CheckID(ID):
	#checks if the passed ID already is held in the database
	query = db.select([records]).where(records.columns.ID == ID)
	resultProxy = connection.execute(query)
	results = resultProxy.fetchall()
	if len(results) < 1:
		return True
	else:
		return False

def LoadEntry():
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

def NextResultPage(targetPage):
	driver.implicitly_wait(2)
	try:
		#gets the page number and links
		pageNosParent = driver.find_element_by_class_name('pagination')
		currentPageButton = pageNosParent.find_element_by_class_name('current')
		currentPageText = currentPageButton.text
		#clicks to the next page if the current page has been exhausted
		if str(targetPage) == currentPageText:
			nextButton = driver.find_element_by_class_name('next')
			nextButton.click()
			return 1
		try: 
			#if the target page is one of the page links clicks the link
			targetLink = driver.find_element_by_link_text(targetPage)
			targetLink.click()
			return 1
		except:
			#if rerunning the program with an existing database clicks 
			if targetPage == 0:
				nextButton = driver.find_element_by_class_name('next')
				nextButton.click()
			#clicks onto the furtherst most page link towards the desired page
			else:
				if currentPageText == '1':
					pageLink = driver.find_element_by_xpath('/html/body/div[7]/div[9]/table[1]/tbody/tr[1]/td/table/tbody/tr/td/div/a[6]')
					pageLink.click()
				else:
					pageLink = driver.find_element_by_xpath('/html/body/div[7]/div[9]/table[1]/tbody/tr[1]/td/table/tbody/tr/td/div/a[7]')
					pageLink.click()
			return 1
	except:
		pass
	#if an ad appears reloads the page
	try:
		dismissButton = driver.find_element_by_xpath('/html/body/div/div[1]/div[1]')
		driver.refresh()
		return 1
	except:
		pass
	return -1

def ScrapeEntry():
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
	data = [None] * 22
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
	if entryData[5] == None:
		query = db.insert(records).values(ID=str(entryData[0]))
	else:	
		query = db.insert(records).values(ID=str(entryData[0]), CaseNumber=str(entryData[5]), Date=ConvertToDate(entryData[2]), Name=str(entryData[6]), Country=str(entryData[1]), Court=str(entryData[3]), Judge=str(entryData[4]), Gender=str(entryData[7]), Age=holdAge, CoDefendants=str(entryData[9]), BailPosition=str(entryData[10]), Charges=str(string_token.join(entryData[11])), Sentances=str(string_token.join(entryData[12])), Order=str(entryData[13]), PublicProtectionSentence=str(entryData[15]), SentencingConsiderations=str(entryData[14]), MitigatingAndAggravatingFactors=str(entryData[18]), Sentenced=str(entryData[19]), TotalSentence=str(entryData[16]), EarliestReleaseDate=ConvertToDate(entryData[17]) , ProsecutingAuthority=str(entryData[20]), PoliceArea=str(entryData[21]))
	commit = engine.execute(query)

def CheckForCaptcha():
	try:
		findCaptcha = driver.find_element_by_id('captcha')
		return True
	except:
		return False

startTime = datetime.datetime.now()
print('Start Time: ' + str(startTime))

Chrome(executable_path='C:/WebDriver/bin/chromedriver')
driver = Chrome()
Login() 

#sets up the table
engine = db.create_engine('sqlite:///SQLite-Test-Database.db')
connection = engine.connect()
metadata = db.MetaData()
foundTable = CheckingForTable(engine)
if foundTable == False:
	records = CreateTable()
else:
	records = db.Table('records', metadata, autoload=True, autoload_with=engine)

captchaCheck = False
count = 0
nextPage = 0
targetPage = 0
currentPage = 1
exceptionCount = 0
while count < 10000:
	try:
		if nextPage == 0:
			FillSearchFields() 
		nextPage = 0
		currentPage = driver.find_element_by_class_name('current').text
		entryID = LoadEntry()
		captchaCheck = CheckForCaptcha()
		if captchaCheck == True:
			captchaCheck = False
			nextPage == 0
			driver.quit()
			driver = Chrome()
			driver.implicitly_wait(2)
			Login()
		elif str(entryID) != '-1':
			targetPage = currentPage
			print('targetPage: ' + str(targetPage))
			scrapedEntryData = ScrapeEntry()
			valuesEntryData = ExtractValuesFromData(scrapedEntryData, entryID)
			print(valuesEntryData)
			if EndDate in valuesEntryData[2]:
				print('Scraped all records within specified time frame')
				break
			PassInEntry(records, valuesEntryData)
			count = count + 1
			print('count: '+ str(count))
		else:
			nextPage = NextResultPage(targetPage)
			if nextPage == -1:
				break
		exceptionCount = 0
	except:
		exceptionCount = exceptionCount + 1
		print('exception check')
		if exceptionCount > 3:
			print('EXCEPTION FOUND!')
			break


endTime = datetime.datetime.now()
elapsedTime = endTime - startTime
print('End Time: ' + str(endTime))
print('Elapsed Time: ' + str(elapsedTime))
driver.quit()