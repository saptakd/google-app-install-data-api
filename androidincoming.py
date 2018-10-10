import os
import csv
import datetime
import codecs
import subprocess
import MySQLdb
import logging

logging.basicConfig(filename='Googleincoming.log',filemode='w',level=logging.DEBUG)

def readFile (fileName,folderPath):
	csvFile = codecs.open('reports/'+folderPath+fileName,'rU','utf-16')
	csvReader = csv.reader(csvFile)
	csvData = list(csvReader)
	return csvData;

def insertintoDb(datatbp,appDetails) :
	
	for index in range(len(datatbp[0])):
		if(datatbp[0][index] == 'Daily Device Installs'):
			deviceinstallsIndex = index
			#print deviceinstallsIndex

		elif(datatbp[0][index] == 'Daily Device Uninstalls'):
			deviceuninstallsIndex = index
			#print deviceuninstallsIndex

		elif(datatbp[0][index] == 'Active Device Installs'):
			activedeviceIndex = index
			#print activedeviceIndex
		elif(datatbp[0][index] == 'Total User Installs'):
			totalinstallsindex = index				
# Open database connection
	#db = MySQLdb.connect("localhost","root","justdial","saptak" )
	db = MySQLdb.connect("172.29.0.218","saptakd","saptak!@#","db_mahi" )
	
	if(db):
		logging.info("Connection Successful "+currentDate);
	else:
		logging.error("connection not sucessfully "+currentDate);
		

# prepare a cursor object using cursor() method
	cursor = db.cursor()
	for index in range(1,len(datatbp)):
		dateprint = datatbp[index][0]
		#dateprint =  datetime.datetime.strptime(datatbp[index][0],"%Y-%m-%d").strftime("%d-%m-%y");	
		if(appDetails == 'jdlite'):	
			query = "UPDATE db_mahi.install_report SET android_in_jdlite='"+datatbp[index][deviceinstallsIndex]+"', android_un_jdlite='"+datatbp[index][deviceuninstallsIndex]+"', active_jdlite='"+datatbp[index][activedeviceIndex]+"', total_jdlite_installs='"+datatbp[index][totalinstallsindex]+"' WHERE date='"+dateprint+"';"
		else:
			query = "UPDATE db_mahi.install_report SET android_in_jdapp='"+datatbp[index][deviceinstallsIndex]+"', android_un_jdapp='"+datatbp[index][deviceuninstallsIndex]+"', active_jdapp='"+datatbp[index][activedeviceIndex]+"' WHERE date='"+dateprint+"';"
			
		#print query;
# execute SQL query using execute() method.
		output = cursor.execute(query)
		db.commit()
		if (output != 1):
			logging.error("Query execution failed "+currentDate)
		else:
			logging.info("successfully inserted "+currentDate);
	
	updateTotal = "UPDATE db_mahi.install_report SET total_in = android_in_jdapp + android_in_jdlite , total_un= android_un_jdapp + android_un_jdlite, total_active= active_jdapp + active_jdlite ;"
	totalOutput = cursor.execute(updateTotal);
	db.commit()
	if(totalOutput != 1):
		logging.error("total update failed "+currentDate)
	else:
		logging.info("total successfully updated "+currentDate)	
# Fetch a single row using fetchone() method.
	#data = cursor.fetchone()
	db.close()	
	return;

todaysDate = datetime.datetime.now().strftime ("%d")
currentDate = datetime.datetime.now().strftime ("%Y-%m-%d")
currentMonth = datetime.datetime.now().strftime ("%Y%m")
twodaysAgo = datetime.datetime.now() - datetime.timedelta(days=2)
twodaysAgo = twodaysAgo.strftime("%Y-%m-%d")

if(todaysDate == '01' or todaysDate == '02' or todaysDate == '03'):
	today = datetime.date.today()
  	first = today.replace(day=1)
 	lastMonth = first - datetime.timedelta(days=1)
 	currentMonth = lastMonth.strftime("%Y%m")


jdliteOverview = 'installs_com.justdial.jdlite_' + currentMonth + '_overview.csv'
jdappOverview = 'installs_com.justdial.search_' + currentMonth + '_overview.csv'

#jdliteOverview = 'installs_com.justdial.jdlite_201702_overview.csv'
#jdappOverview = 'installs_com.justdial.search_201702_overview.csv'

#print jdliteOverview

liteProcess = os.system("./google-cloud-sdk/bin/gsutil cp gs://pubsite_prod_rev_1048811653366xxxxxxx/stats/installs/"+ jdliteOverview +" reports/jdlite")

searchProcess = os.system("./google-cloud-sdk/bin/gsutil cp gs://pubsite_prod_rev_1048811653366xxxxxxx/stats/installs/"+ jdappOverview + " reports/jdsearch")

#print searchProcess

jdliteData = readFile(jdliteOverview, 'jdlite/')
jdsearchData = readFile(jdappOverview, 'jdsearch/')


if jdliteData != None and jdsearchData != None:
	insertintoDb(jdliteData,'jdlite')
	insertintoDb(jdsearchData,'jdapp')		
else:
	print "Inadequate Data"


