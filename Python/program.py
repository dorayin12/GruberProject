#This is the program for the entire process
#Seperated jobs include download, unzip
#The local path is C:\myproject\API


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import time
import zipfile
import glob, os, os.path
import MySQLdb
import csv
import time
import sys


#days
lastweek  = datetime.now() - timedelta(days=130)  #last week today
day1      = lastweek.strftime('%m/%d/%Y') #end
yesterday = datetime.now() - timedelta(days = 131)  #last week 
day2      = yesterday.strftime('%m/%d/%Y') #start
name_date = yesterday.strftime('%m-%d-%Y %I_%M%p')


#browser set up
#phantomjs = 'C:\myproject\API\phantomjs.exe'
#browser = webdriver.PhantomJS(phantomjs)
chromeOptions = webdriver.ChromeOptions()
prefs = {'download.default_directory' : 'C:\myproject\API'} #change default location
chromeOptions.add_experimental_option('prefs',prefs)
chromedriver = 'C:\myproject\API\chromedriver.exe'
browser = webdriver.Chrome(chromedriver, chrome_options=chromeOptions)
browser.get('https://app.fitabase.com/DownloadData/CreateBatch/f4def67f-9081-4534-bbf4-3741be7d59df')


#log in
username = browser.find_element_by_id('UserName')
password = browser.find_element_by_id('Password')
username.send_keys('....')
password.send_keys('....')
login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
login_attempt.submit()

#fill the form
browser.find_element_by_id('Name').clear()
browser.find_element_by_id('StartDate').clear()
browser.find_element_by_id('EndDate').clear()

exportname = browser.find_element_by_id('Name')
startdate = browser.find_element_by_id('StartDate')
enddate = browser.find_element_by_id('EndDate')
exportname.send_keys('Export-'+ name_date)
startdate.send_keys(day2)
enddate.send_keys(day1)


browser.find_element_by_id('batchParam_IncludeFitbitStepsMinutesNarrow').click()
browser.find_element_by_id('batchParam_IncludeFitbitIntensityMinutesNarrow').click()
##browser.find_element_by_id('batchParam_IncludeFitbitCaloriesMinutesNarrow').click()
browser.find_element_by_id('batchParam_IncludeFitbitSleepLogs').click()
##browser.find_element_by_id('batchParam_IncludeFitbitWeightLogs').click()
##browser.find_element_by_id('batchParam_IncludeFitbitMETsMinutesNarrow').click()
##browser.find_element_by_id('batchParam_IncludeFitbitHeartRateRawSesconds').click()
##browser.find_element_by_id('batchParam_IncludeFitbitStepsMinutes').click()
##browser.find_element_by_id('batchParam_IncludeFitbitIntensityMinutes').click()
##browser.find_element_by_id('batchParam_IncludeFitbitCaloriesMinutes').click()
##browser.find_element_by_id('batchParam_IncludeFitbitMETsMinutes').click()
##browser.find_element_by_id('batchParam_IncludeFitbitStepsHourly').click()
##browser.find_element_by_id('batchParam_IncludeFitbitIntensityHourly').click()
##browser.find_element_by_id('batchParam_IncludeFitbitCaloriesHourly').click()
##browser.find_element_by_id('batchParam_IncludeFitbitDailyActivity').click()
##browser.find_element_by_id('batchParam_IncludeFitbitDailySteps').click()
##browser.find_element_by_id('batchParam_IncludeFitbitDailyIntensity').click()
##browser.find_element_by_id('batchParam_IncludeFitbitDailyCalories').click()
##browser.find_element_by_id('batchParam_IncludeFitbitDailySleep').click()

browser.find_element_by_xpath("//*[@class='btn']").click()

#submit 
project_create = browser.find_element_by_xpath("//*[@type='submit']")
project_create.submit()
print 'Project created successfully'
print 'Wait for 300 seconds to generate the project'
#browser.save_screenshot('C:\myproject\API\screen.jpg')
#postpone for a minute to get the link
time.sleep(300) #two options take ca.30s

#download
download_page = browser.get('https://app.fitabase.com/DownloadData/Project/f4def67f-9081-4534-bbf4-3741be7d59df')
html          = browser.page_source
soup          = BeautifulSoup(html)
variable      = soup.find_all('a')[5]
link          = 'https://app.fitabase.com' + variable.attrs['href']
browser.get(link)
print 'Download!'

#unzip file and delete zip file
#find zip file
os.chdir('C:\myproject\API')
filename = glob.glob("*.zip")
new = str(filename).strip("'[]'") #xxx.zip
##unzip
path = 'C:\myproject\API\\' + new
zip_ref = zipfile.ZipFile(path, 'r')  #Got error, IOError: [Errno 2] No such file or directory: 'C:\\myproject\\API\\'
zip_ref.extractall('C:\myproject\API')
zip_ref.close()
print new + ' is unzipped'

os.remove(path)

#upload files to database & delete files
#file name
csvfiles = glob.glob(r'C:\myproject\API\*.csv')
new1 = str(csvfiles[0]).strip("''") #with path and extension
new2 = os.path.splitext(os.path.basename(new))[0] #only file name

#connector
conn = MySQLdb.connect (user="root",
                        host="localhost",
                        db="fitabase")
cursor = conn.cursor()


#intensity
cursor.execute("INSERT INTO history (name) VALUES (%s)", {new2})
int_data = csv.reader(file(new1,'rU'))

int_data.next()
for row in int_data:
    gettime = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S %p')
    gettime = gettime.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO intens(record_ID, ID, in_time, intensity)' \
                   'VALUES(LAST_INSERT_ID(), %s, %s, %s)', (row[0], gettime, row[2]))

conn.commit()
print "Intensity uploaded!"
os.remove(new1)


#step
filename = glob.glob(r'C:\myproject\API\*.csv')
new1 = str(filename[0]).strip("''") #with path and extension
int_data = csv.reader(file(new1,'rU'))

int_data.next()
for row in int_data:
    gettime = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S %p')
    gettime = gettime.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO step(ID, st_time, step)' \
                   'VALUES(%s, %s, %s)', (row[0], gettime, row[2]))

conn.commit()
os.remove(new1)
print "Step uploaded!"


#sleep
filename = glob.glob(r'C:\myproject\API\*.csv')
new1 = str(filename[0]).strip("''") #with path and extension
int_data = csv.reader(file(file(new1,'rU'))

int_data.next()
for row in int_data:
    gettime = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S %p')
    gettime = gettime.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO sleep(ID, sl_time, sleep, logid)' \
                   'VALUES(%s, %s, %s, %s)', (row[0], gettime, row[2], row[3]))

conn.commit()
os.remove(new1)
print "Sleep uploaded!"
