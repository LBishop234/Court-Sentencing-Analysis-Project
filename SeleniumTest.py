import time, requests, certifi, ssl
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import urllib.request as urllib2

def FillSearchFields():
	
	Chrome(executable_path='C:/WebDriver/bin/chromedriver')
	
	with Chrome() as driver:
		driver.get("https://www.thelawpages.com/court-cases/court-case-search.php?mode=3")
		assert len(driver.window_handles) == 1
		WebDriverWait(driver, 10).until(EC.title_is("Crown Court Cases Results Criminal Sentences Crime Offence Judge Solicitor Barrister"))
		print("Found thelawpages.com court case advanced search")

		popupButton = driver.find_element_by_id("submitButtons")
		driver.implicitly_wait(5)
		popupButton.click()

		cal1 = driver.find_element_by_id("cal1")
		cal2 = driver.find_element_by_id("cal12")
		courtType = driver.find_element_by_id("c_type")

		cal1.click()
		currentSelected1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
		backYear1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[1]")
		backMonth1 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
		backYear1.click()
		while(currentSelected1.text != "May, 2019"):
			backMonth1.click()
		selectDay1 = driver.find_element_by_xpath("/html/body/div[7]/div[9]/table/tbody/tr/td/form/table/tbody/tr[1]/td/div/div/table/tbody/tr[4]/td[3]")
		selectDay1.click()

	  #time.sleep(2)
		cal2.click()
		currentSelected2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[1]/td")
		backMonth2 = driver.find_element_by_xpath("/html/body/div[8]/table/thead/tr[2]/td[2]")
		while(currentSelected2.text != "May, 2020"):
			backMonth2.click()
		selectDay2 = driver.find_element_by_xpath("/html/body/div[7]/div[9]/table/tbody/tr/td/form/table/tbody/tr[1]/td/div/div/table/tbody/tr[11]/td[3]/label/input")
		selectDay2.click()

		#time.sleep(2)
		courtType.send_keys("Crown Court")
		driver.implicitly_wait(5)
		court = driver.find_element_by_id("court_location")
		court.send_keys("Leeds Crown Court")
		driver.implicitly_wait(5)
		searchButton = driver.find_element_by_id("submitButton")
		searchButton.click()

		driver.implicitly_wait(10)
		thisUrl = driver.current_url
		print("Searched")
		return thisUrl

def LoadEntry( tableUrl ):
	testUrl = "https://www.thelawpages.com/"
	loginData = dict(login='LMBishop', password='Canford2014B')
	session = requests.session()
	r = session.post(testUrl, data=loginData)
	print(r)

thisUrl = FillSearchFields()
LoadEntry(thisUrl)