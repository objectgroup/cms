#!/usr/bin/python3

import pytz
import os
import csv
import datetime
from itertools import tee, islice, chain 
import re
import cmsc
from operator import itemgetter
import shutil

websiteName = cmsc.websiteName
websiteDomain = cmsc.websiteDomain
websiteURL = cmsc.websiteURL
websiteEmail = cmsc.websiteEmail
websiteDescription = cmsc.websiteDescription
websiteMetaIndex = cmsc.websiteMetaIndex
websiteLanguage = cmsc.websiteLanguage
faviconURL = cmsc.faviconURL
faviconPathIndex = cmsc.faviconPathIndex
faviconPathYear = "../" + faviconPathIndex
faviconPathMonth = "../../" + faviconPathIndex
styleSheetPathIndex = cmsc.styleSheetPathIndex
styleSheetPathYear = "../" + styleSheetPathIndex
styleSheetPathMonth = "../../" + styleSheetPathIndex
rssFileName = cmsc.rssFileName
rssFilePathMonth = "../../" + rssFileName
rssFilePathYear = "../" + rssFileName
numberOfRssItems = cmsc.numberOfRssItems
footerText = cmsc.footerText

yearDescending = []

def build (fileName, appendText):
	with open (fileName, 'a') as append_file: 
		append_file.write(appendText)

def moveDirectoryDown(newDirectory):
    currentDir = os.getcwd()
    nextDirectory = os.path.join(currentDir, newDirectory)
    if (os.path.isdir(newDirectory)):
        print (newDirectory + " directory exists, changing directory to it")
        os.chdir(nextDirectory)
        currentDirectory = os.getcwd()
        return currentDirectory
    else:
        print (newDirectory + " directory does not exist")

def moveDirectoryUp():
	os.chdir("..")
	currentDirectory = os.getcwd()
	return currentDirectory

def createDictionaryForMonths():
	newDirectory = "blogs"
	currentDirectory = moveDirectoryDown(newDirectory)
	monthsDictionary = {}

	for blog in os.listdir(currentDirectory):
		if checkFileFormat(blog):
			print ("file format passed: " + blog)
		
			fileTime = splitFileName(blog)
			year = fileTime["year"]
			monthNumber = fileTime["monthNumber"]
			newFile = str(fileTime["year"]) + "_" + str(fileTime["monthNumber"])
			# add to monthDictioanry what we can deduce for the
			# file name - like year, month number, filename, and new
			# filename that will be created. 
			monthDictionary = {"fileName": blog, "year": year, "monthNumber": monthNumber, "newFileName": newFile}
			# add to the monthDictionary the month name
			monthDictionary = identifyMonth(monthDictionary)
			# add to the monthDictionary the page title name
			monthDictionary["title"] = "Notes for " + str(monthDictionary["monthText"]) + " " + str(monthDictionary["year"])
			# add to monthDictionary the bredcrumb html
			monthDictionary = createMonthsBreadcrumb(monthDictionary)
			# add this monthdictionary to the dictionary of all months
			monthsDictionary[monthDictionary["fileName"]] = monthDictionary
		else:
			print ("file format failed: " + blog)
	# work out the future and past links for each month and add
	# it to each entry as navigation 
	monthsDictionary = orderedMonths(monthsDictionary)
	# add the meta files to the monthDictionary
	monthsDictionary = createMeta(monthsDictionary)
	return monthsDictionary

def checkFileFormat(blogFileName):
	# checks for a pattern in the file name of:
	#  a year range seperated by a hyphen then 1-12 for the month  
	pattern = r"^20[0-9]{2}-([1-9]|1[0-2])$"
	if re.match(pattern, blogFileName):
		return True
	else:
		return False

def splitFileName(blogFileName):
	# split the file name on the hyphen to get year and month seperately
	post = blogFileName.split("-")
	postYear =  post[0]
	postMonth = post[1]
	fileTime = {"fileName": blogFileName, "year": int(postYear), "monthNumber": int(postMonth)}
	return fileTime

def identifyMonth(monthDictionary):
	months = {1: "January ", 2: "February ", 3:"March ", 4:"April ", 5:"May ", 6:"June ", 7:"July ", 8:"August ", 9:"September ", 10:"October ", 11:"November ", 12:"December "}
	for month in months:
		if month == monthDictionary["monthNumber"] :
			print ("Check for correct month identification: month " + str(month) + " identified as " + months[month] + str(monthDictionary["year"]))
			# add to the dictionary fileTime the monthText
			monthDictionary["monthText"] = months[month]
			return monthDictionary

def createMonthsBreadcrumb(monthDictionary):
	# breadcrumb text
	# defines a dictionary with key of filename
    # and value of a string that is the 
	# html of the breadcrumb which is 
    # <li><a href="../../">home</a></li> 
    # <li><a href="../">2023 notes</a></li>
    # <li>February 2023</li>
	opening = "<li><a href='../../'>home</a></li><li><a href='../'>"
	middle = " notes</a></li><li>"
	ending = "</li>"
	monthDictionary["breadcrumb"] = opening + str(monthDictionary["year"]) + middle + monthDictionary["monthText"] + str(monthDictionary["year"]) + ending
	return monthDictionary

def previousAndNext(iterable):
	prevs, items, nexts = tee(iterable, 3)
	prevs = chain([None], prevs)
	nexts = chain(islice(nexts, 1, None), [None])
	return zip(prevs, items, nexts)

def sameYear(year1, year2):
	if year1 == year2:
		return "yes"
	else:
		return "no"

def orderedMonths(monthsDictionary):
	previousEntry = "previous"
	nextEntry = "next"
	year = 0
	month = 1
	quote = "'"
	slash = "/"
	slashIndex = "/index.html"
    # put together the month and year to create a two element list  
    # then order the year blog first with the month blogs second 
	yearsMonthTuple = []
	for fileName in monthsDictionary:
		fileYear = monthsDictionary[fileName]["year"]			
		fileMonth = monthsDictionary[fileName]["monthNumber"]			
		yearMonth = (fileYear, fileMonth)
		yearsMonthTuple.append(yearMonth)
	yearsMonthsSorted = sorted(yearsMonthTuple, key=itemgetter(0,1))
	print (yearsMonthsSorted)
	for previous, current, thenext in previousAndNext(yearsMonthsSorted):
		filename = str(current[year]) + "-" + str(current[month])
		monthsDictionary[filename].update({"navigation":{}})
		print(f"current: {current},  previous: { previous},  next: {thenext}")

		if previous == None:
			monthsDictionary[filename]["navigation"].update({previousEntry: None})
		if thenext == None:	
			monthsDictionary[filename]["navigation"].update({nextEntry : None})
		# there is a previous month
		if previous != None:
			monthsDictionary[filename]["navigation"].update({previousEntry: quote + websiteURL + slash + str(previous[year]) + slash + str(previous[month]) + slashIndex + quote})
		# there is a next month
		if thenext != None:
			monthsDictionary[filename]["navigation"].update({nextEntry: quote + websiteURL + slash + str(thenext[year]) + slash + str(thenext[month]) + slashIndex + quote})
		print("MONTHS DICTIONARY" , monthsDictionary)
	return monthsDictionary

def createMeta(monthsDictionary):
	# read the meta.csv and Blogs files into data structures #
	with open ("../meta.csv", 'r') as csvfile: 	
		reader = csv.reader(csvfile)

	# loop through each line of the meta.csv 
	# if it's filename matches with the monthDictionary filename
	# then add values of metatitle and metaDescription to the dictionary
		for row in reader:
			csvFilename = row[0]
			metatitle = row[1] 
			metaDescription = row[2] 
			monthsDictionary[csvFilename]["metaTitle"] = metatitle
			monthsDictionary[csvFilename]["metaDescription"] = metaDescription
	return monthsDictionary


def createDictionaryForYears(monthsDictionary):
	yearsDictionary = {}
	tempYearsDictionary = {}
	# I'm using the monthsDictionary to identify years
	# and their associated months. 
	# I loop throught the list of filenames in monthsDictionary
	# each entry is a month 
	# and create a new dictionary where year is the key
	# and the values are:
	# a list of months for that year with key "months"
	for filename in monthsDictionary:
		year = monthsDictionary[filename]["year"]
		monthNumber = monthsDictionary[filename]["monthNumber"]
		monthText = monthsDictionary[filename]["monthText"]
		monthFilename = monthsDictionary[filename]["fileName"]
		if year in tempYearsDictionary:
			tempYearsDictionary[year][monthNumber] = [monthFilename, monthText, monthNumber]
		else:
			tempYearsDictionary[year] = {monthNumber: [monthFilename, monthText, monthNumber]}
			yearsDictionary[year] = {}
	
	yearDescendingMonths = {}		
	for year in tempYearsDictionary:
		yearSorted = sorted(tempYearsDictionary[year], reverse=True)
		tempList = []
		for month in yearSorted:
			monthsAscending = tempYearsDictionary[year][month]
			tempList.append(monthsAscending)
		yearsDictionary[year]["monthAscending"] = tempList
	# create a global list of the years in Descending order 
	# (most recent year first)
	for year in yearsDictionary:
		yearDescending.append(year)
		yearDescending.sort(reverse=True)
	
	# this is how you retrive the results of the ascending sorting of months
	for year in yearsDictionary:
		print (year)
		for month in  yearsDictionary[year]["monthAscending"]:
			print ("filename: " + str(month[0]))
			print ("month text: " + str(month[1]))
			print ("month number: " + str(month[2]))  
			
	# yearsDictionary is a data structure and each year has: 
	# a dictionary of its month number key 
	# and month text as value ordered descending of the month numbers
	# a dictionary of its month number as key 
	# and filename for that month as value ordered descending the month numbers
	# the breadcrumb for that year
  	# the meta data for that year
	# the navigation previous and next for that year

	# now add to the yearsDictionary:
	# a list of filenames for that year with key "year"
	# a breadcrumb for that year with key 'breadcrumb'
	# a title for that year with key 'title'
	# a previous and next year with key 'navigation'
	# the meta tags data for that year
	for year in yearsDictionary:
		yearsDictionary[year]["title"] = "Notes for " + str(year)
	
	yearsDictionary = createYearsBreadcrumb(yearsDictionary)
	yearsDictionary = createYearMeta(yearsDictionary)
	yearsDictionary = orderedYears(yearsDictionary)
	return yearsDictionary

def createYearMeta(yearsDictionary):
	# read the meta.csv and Blogs files into data structures #
	with open ("../meta-year.csv", 'r')	as csvfile: 
		reader = csv.reader(csvfile)

	# loop through each line of the meta.csv 
	# if it's filename matches with the monthDictionary filename
	# then add values of metatitle and metatags to the dictionary
		for column in reader:
			cvsYear = column[0]
			metatitle = column[1]
			metatag = column[2]
			for year in yearsDictionary:
				if str(year) == str(cvsYear):
					yearsDictionary[year]["metaTag"] = metatag
					yearsDictionary[year]["metaTitle"] = metatitle
	return yearsDictionary

def createYearsBreadcrumb(yearsDictionary):
	# breadcrumb text
	# defines a dictionary with key of filename
    # and value of a string that is the 
	# html of the breadcrumb which is 
	# <nav>
	#   <ol class="breadcrumb">
    # 		<li><a href="../">home</a></li> 
    # 		<li>2023 notes</li>
	#   </ol>
	# </nav>
	opening = '<nav><ol class="breadcrumb"><li><a href="..">home</a></li><li>'
	ending = " notes</li></ol></nav>"
	for year in yearsDictionary:
		yearsDictionary[year]["breadcrumb"] = opening + str(year) + ending
	return yearsDictionary

def orderedYears(yearsDictionary):
	# the keys function is creating a list of years, and sorting
	# finding the max and min and number 
	minYear = min(yearsDictionary.keys())
	maxYear = max(yearsDictionary.keys())
	numberOfYears = len(yearsDictionary)
	sortedYears = sorted(yearsDictionary.keys())
	
	for year in sortedYears:
		if numberOfYears == 1:
			yearsDictionary[year]["navigation"] = {"past": None, "future": None}
		else:
			if year == minYear:
				yearsDictionary[year]["navigation"] = {"future": sortedYears[sortedYears.index(year) + 1], "past": None}
			elif year == maxYear:
				yearsDictionary[year]["navigation"] = {"future": None, "past": sortedYears[sortedYears.index(year) - 1]}
			else:
				yearsDictionary[year]["navigation"] = {"future": sortedYears[sortedYears.index(year) + 1], "past": sortedYears[sortedYears.index(year) - 1]}
	return yearsDictionary


def makeMonth(monthsDictionary):

	breadcrumbStart= '<nav><ol class="breadcrumb"><li><a href="../../index.html">home</a></li><li><a href="../index.html">'
	breadcrumbMiddle = ' notes</a></li><li>'
	breadcrumbEnd = '</li></ol></nav>'
	
	titleStart = '<main><article>'

	for monthDictionary in monthsDictionary:
		# For each month there is a blog post for
		# build up a list that constains all of the data in the 
		# order it will be added to the html file. 
		# The list is called blogOrder. 
		blogOrder = []
		
		# add the locations that make up the head
		metatitle = monthsDictionary[monthDictionary]['metaTitle']
		metaDescription = monthsDictionary[monthDictionary]['metaDescription']
		monthHead = makeHead(styleSheetPathMonth, faviconPathMonth, metaDescription, metatitle)	
		blogOrder.append(monthHead)

		# start the body and titles
		breadcrumbYear = str(monthsDictionary[monthDictionary]['year'])
		monthYear = monthsDictionary[monthDictionary]["monthText"] + " " + breadcrumbYear
		bodyStart = '<header><h1>' + monthYear + '</h1></header>'	
		blogOrder.append(bodyStart)
		# add the locations that make up the breadcrumb trail
		blogOrder.append(breadcrumbStart)
		blogOrder.append(breadcrumbYear)
		blogOrder.append(breadcrumbMiddle)
		blogOrder.append(monthYear)
		blogOrder.append(breadcrumbEnd)
		blogOrder.append(titleStart)
		
		# This is the list of contents to end the html file 
		blogOrderEnd = []
		previousEntry = "previous"
		nextEntry = "next"	
		navigationStart = '</article><nav>'
		navigationPastStart = '<h4 class="past"><a href='
		navigationPastEnd = '>past</a></h4>'
		navigationFutureStart = '<h4 class="future"><a href='
		navigationFutureEnd = '>future</a></h4>'
		navigationEnd = '</nav></main>'
	
		past = monthsDictionary[monthDictionary]["navigation"][previousEntry]
		future = monthsDictionary[monthDictionary]["navigation"][nextEntry]
		if past is not None or future is not None:
 			blogOrderEnd.append(navigationStart)

		if past is not None:
			blogOrderEnd.append(navigationPastStart)
			linkToPast = monthsDictionary[monthDictionary]["navigation"]['previous']
			blogOrderEnd.append(linkToPast)
			blogOrderEnd.append(navigationPastEnd)
		
		if future is not None:
			blogOrderEnd.append(navigationFutureStart)
			linkToFuture = monthsDictionary[monthDictionary]["navigation"]['next']
			blogOrderEnd.append(linkToFuture)
			blogOrderEnd.append(navigationFutureEnd)

		if past is not None or future is not None:
 			blogOrderEnd.append(navigationEnd)
		
		monthFooter = makeFooter(rssFilePathMonth)
		blogOrderEnd.append(monthFooter)
		
		# add all the html data to the html file
		newFileName = monthsDictionary[monthDictionary]["newFileName"] 
		with open(newFileName, 'w') as f:
		# write to the new file the header and breadcrumb and title text html
			for entry in blogOrder:
	 			f.write(entry)
			# identify the filename to open the plain text notes/blog
			fileName = monthsDictionary[monthDictionary]["fileName"]
			# open and wrap html text to this file and return it as a list 
			fileContent = wrapHtml(fileName)
			# write this list of html wrapped text to the new file 
			for content in fileContent:
				f.write(content)
			# write to the new file all the footer and navigation html
			for entry in blogOrderEnd:
	 			f.write(entry)

def makeYear(yearDictionary):

    # the yearDictionary has key "year" and for each year there are values:
	# 'months' is the list of month numbers for this year
	# "filename" with a list of the filenames in that year
 	# "title" which is "Notes for [year]"
	# "navigation" which is a dictionary of future and past keys each with the year appropriate. 
	# "breadcrumb" which is the whole string of html that gives the breadcrumb trail. <ol>
 	# "metatag" the metatag in column 2 of the meta-year.csv
	# "metatitle" is the meta title in column 1 if the meta-year.csv 

	# define the header text in html and add in the meta text 
	startHeader = '<header><h1>'
	endHeader = '</h1></header>'	
	
	startMain = '<main>'
	startArticle = '<article>'
	startMonthHeading = '<h3><a href="'
	middleMonthHeading = '">'
	endMonthHeading = '</a></h3>'
	endArticle = '</article>'
	navStart = '<nav><h4 class="newer"><a href="'
	endMain = '</main>'
	
	for year in yearDictionary:
		blogOrder = []
		blogOrderEnd = []
		# add the text that makes up the head
		metatitle = yearDictionary[year]['metaTitle']
		metatag = yearDictionary[year]['metaTag']
		monthHead = makeHead(styleSheetPathYear, faviconPathYear, metatag, metatitle)	
		blogOrder.append(monthHead)
		blogOrder.append(startHeader)
		title = yearDictionary[year]['title']
		blogOrder.append(title)
		blogOrder.append(endHeader)
		breadcrumb = yearDictionary[year]['breadcrumb']
		blogOrder.append(breadcrumb)
		blogOrder.append(startMain)
		
		future = yearDictionary[year]['navigation']['future']
		past = yearDictionary[year]['navigation']['past']

		navigationStart = '<nav>'
		navigationPastStart = '<h4 class="past"><a href="../'
		navigationPastEnd = '">past</a></h4>'
		navigationFutureStart = '<h4 class="future"><a href="../'
		navigationFutureEnd = '">future</a></h4>'
		navigationEnd = '</nav></main>'

		if past is not None or future is not None:
			blogOrderEnd.append(navigationStart)

		if past is not None:
			blogOrderEnd.append(navigationPastStart)
			linkToPast = yearDictionary[year]["navigation"]['past']
			blogOrderEnd.append(str(linkToPast))
			blogOrderEnd.append(navigationPastEnd)
		
		if future is not None:
			blogOrderEnd.append(navigationFutureStart)
			linkToFuture = yearDictionary[year]["navigation"]['future']
			blogOrderEnd.append(str(linkToFuture))
			blogOrderEnd.append(navigationFutureEnd)
		
		if past is not None or future is not None:
			blogOrderEnd.append(navigationEnd)

		blogOrderEnd.append(endMain)
		htmlEnd = makeFooter(rssFilePathYear)
		blogOrderEnd.append(htmlEnd)
	    	
		# add all the html data to the html file
	    # this is how you retrive the results of the ascending sorting of months
		newFileName = str(year)
		with open(newFileName, 'a') as f:
			for entry in blogOrder:
				f.write(entry)
			for month in yearDictionary[year]["monthAscending"]:
				filename = str(month[0])
				monthText = str(month[1]) + str(year)
				monthNumber = str(month[2])
				f.write(startArticle)
				f.write(startMonthHeading)
				f.write(monthNumber)
				f.write(middleMonthHeading)
				f.write(monthText)
				f.write(endMonthHeading)
				# for the identified month wrap the text in html 
				# and the return text is in a list
				blogEntry = wrapHtml(filename)
				# then loop through the list to add it to the year html page
				for fileContent in blogEntry:
					f.write(fileContent)
				f.write(endArticle)
			for entry in blogOrderEnd:
				f.write(entry)

def makeDirectory(yearDictionary, monthsDictionary, rssDictionary):
	# if the notes directory already exists
	# rename it to notes plus the current year month day and hour
	# and then create a new notes directory
	# if there is no notes directory then make one
	currentDirectory = moveDirectoryUp()
	notes = "notes"
	notesDirectory = os.path.join(currentDirectory, notes) 
	if (os.path.isdir(notesDirectory)):
		currentTime = datetime.datetime.now()
		os.rename(notes, notes+"-"+str(currentTime))
		os.mkdir(notes)
	else:
		os.mkdir(notes)
	currentDirectory = moveDirectoryDown(notes)

	# make the about.html, the index.html and the rss.xml 
	# in the notes directory		
	makeRSS(rssDictionary)
	# makeIndex always comes after makeRSS because makeRSS calculates 
	# the latest year there is a blog entry for and this is used in index
	# to always link to the latest year page there is an entry for
	makeIndex()
	makeAbout()
		
	# make directory structure in notes directory
	for year in yearDictionary:
		# monthNumber is the second element in the array
		# yearDictionary[year]["monthAscending"]
		monthNumber = 2
		yearDirectory = str(year)
		os.mkdir(yearDirectory)
		moveDirectoryDown(yearDirectory)
		for month in yearDictionary[year]["monthAscending"]:
			monthDirectory = str(month[monthNumber])
			os.mkdir(monthDirectory)
		moveDirectoryUp()
	# move back up to the test-script directory 
	moveDirectoryUp()
	# move files from blogs directory into approates part of the notes directory
	# the fileMove list has three elements: 
	# the first is the file location and two is the destination
	# the third is the filename in its new destination
	fileMove = []
	for year in yearDictionary:
		yearFile = str(year)
		fileMove.append(["blogs/" + yearFile, "notes/" + yearFile])

	for filename in monthsDictionary:
		# add the year files from the blogs directory
		year = str(monthsDictionary[filename]['year'])
		# add the month files from the blogs directory
		newFileName = str(monthsDictionary[filename]['newFileName']) 
		monthNumber = str(monthsDictionary[filename]['monthNumber']) 
		fileMove.append(["blogs/" + newFileName, "notes/" + year + "/" + monthNumber])

	for fileName in fileMove:
		location = 0
		destinationDirectory = 1
		index = 'index.html'
		destination = fileName[destinationDirectory] + "/" + index
		print (fileName[location], destination)
		os.rename(fileName[location], destination)

	currentDirectory = os.getcwd()
	print ("current Directory : ", currentDirectory)
	notes = currentDirectory + "/notes"
	shutil.copytree(notes, "../" + websiteDomain, dirs_exist_ok=True)
	shutil.rmtree(notes)

def LetterDay(dayNumber):
	threeLetterDay = ""
	if dayNumber == 0:
		return "Mon"
	if dayNumber == 1:
		return "Tue"
	if dayNumber == 2:
		return "Wed"
	if dayNumber == 3:
		return "Thu"
	if dayNumber == 4:
		return "Fri"
	if dayNumber == 5:
		return "Sat"
	if dayNumber == 6:
		return "Sun"
			

def createDictionaryForRSS(monthsDictionary, yearDictionary):
			
	moveDirectoryUp()
	# the rss is created from a csv file that has a list of 
	# previous rss pubdates and may contain the current one
	# the csv.py script will identify if the current month and year
	# is present in the pubdate of the last entry of the rss.csv file
	# if present the script will not offer to update the rss.xml
	# but if the current month and year are not present on the 
	# last line of the rss.csv then the script will offer an update
	# of a pubdate with the current date and time 
	
	# a data structure to convert month numbers to a three letter 
	# representation of that month e.g. 1 is Jan 
	# the writtenMonth index is the month number and the list value for
	# that index is the three letter equivalent
	writtenMonth = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]	

	# identify the current month and year
	tz = pytz.timezone('Europe/London')
	currentTime = datetime.datetime.now(tz)
	# the current year is given as a four digigt number e.g. 2026 
	currentYear = (str(currentTime.year))
	# the current month is given as a number 1 to 12
	currentMonth = writtenMonth[currentTime.month]
	# the current day is given as a number 1 to 31
	currentDay = str(currentTime.day)
	currentHour = str(currentTime.hour)
	currentMinute = str(currentTime.minute)
	currentSecond = str(currentTime.second)
	# the currentWeekday is given as a number 1 to 7
	currentWeekday = currentTime.weekday()
	# store the current time in the pubdate format 
	# an example is Mon, 18, May, 2026, 12:30:0 GMT
	rssPubdate = (LetterDay(currentWeekday) + ", " + currentDay + ", " + currentMonth + ", " + currentYear + ", " + currentHour + ":" + currentMinute + ":" + currentSecond + " GMT")

	# a variable that gives the total number of lines in the rss.csv
	totalRSSCSVEntries = 0
	
	# check if rss.csv exists and if so then open it and record the 
	# number of lines in the totalRSSCSVEntries 
	# and if the file does not exist then 
	# set the value of totalRSSCSVEntries to 0
	# which will later be used to create an rss.csv 
	# in the current directory
	if os.path.exists("rss.csv"):	
		with open("rss.csv", "r") as f:
			totalRSSCSVEntries = sum(1 for line in f)
	else:	
		# rss.csv does not exist
		totalRSSCSVEntries = 0

	# set append equal to false as the default 
	# assume there won't be appending unless instructed otherwise
	append = False
	counter = 0
	allRSSentries = {}
	
	# if there are no entries as rss.csv doesn't exist 
	# then offer to add an entry by setting append to true  
	if totalRSSCSVEntries == 0:
		append = True
	# else identify the year and month of each row and
	# create a dictionary with a key of the string year-month
	# where year is a four digit number in string form and
	# month is a number 1 to 12 in string form
	# and the value is the pubdate in string form   
	else:
		with open("rss.csv", "r") as f:
			rsscsvdata = csv.reader(f)
			for row in rsscsvdata:
				counter += 1
				latestRssMonth = row[2].lstrip()
				latestRssYear = row[3].lstrip()
				allRSSentries[latestRssYear + "-" + str(writtenMonth.index(latestRssMonth))] = row
				# if the last pubdate entry in the rss.csv is 
				# this month and year then consider that 
				# no more entries are required at present
				if counter == totalRSSCSVEntries: 
					if latestRssMonth == currentMonth and latestRssYear == currentYear:
						print ("for the date: " +  latestRssYear + "-" + latestRssMonth + " there is already an entry in the rss feed")		
					else:
						print ("there is not already an rss entry for " + latestRssYear + "-" + latestRssMonth)
						append = True
	
	# having identified if there is a new entry to be added 
	# with the append flag check with the use that they want to add it
	if append == True:
		addDate = input("add today's date to the rss feed? (y/n)")
		if addDate == "y" or addDate == "Y" or addDate == "yes" or addDate == "Yes":
			print (str(rssPubdate))
			with open("rss.csv", "a") as f:
				f.write(str(rssPubdate))
				print("new time appended to rss")
		else:
			print ("no new date was added to rss")

	allentrieslist = []
	# the rss.csv is now up to date with entries to be added to the rss.xml 
	# if there are more entries in the rss.csv than defined by the variable
	# numberOfRssItems then pick the latest number of items specified in 
    # numberOfRssItems  
	# else if there are fewer items in the rss.csv than spepecified 
	# by the numberOfRssItems then use what is there
	if os.path.exists("rss.csv"):	
		with open("rss.csv", "r") as f:
			allRssEntries = csv.reader(f)
			for row in allRssEntries:
				allentrieslist.append(row)
			allRssEntriesInCsv = len(allentrieslist)
			if allRssEntriesInCsv > numberOfRssItems:
				latestRSSentries = (allentrieslist[-numberOfRssItems:])
			else:
				latestRSSentries = allentrieslist
	else:
		print("rss.csv doesn't exist")
		return items

	# now the RSS entries are in a latestRSSentries list
	# that has the pubdate seperated into list items, for example
	# ['Mon', ' 18', ' May', ' 2026', ' 12:30:0 GMT']
	# add to each entry a final list item of the year (list item 3)
	# followed by a hyphen followed by the month as a one or two digit 
	# number derived from list item 2. With that final list item
	# it is possible to obtain details from the month or year dictionary 
	# which can be used to construct the rss feed
	moveDirectoryDown("blogs")
	items = {}
	counter = 1
	for entry in latestRSSentries:
		year = entry[3].lstrip()	
		monthInWords = entry[2].lstrip()
		monthInNumbers = str(writtenMonth.index(monthInWords))
		fileName = (year + "-" + monthInNumbers)
		# add all the items from latestRSSentries and monthsDictionary
		# to the dictionary called items 
		threeLetterDay = entry[0].lstrip()
		twoDigitDay = entry[1].lstrip()
		time = entry[4].lstrip()
		pubdate = ("<pubdate>" + threeLetterDay + ", " + twoDigitDay + ", " + monthInWords + ", " + year + ", " + time + "</pubdate>")
		items[fileName] = {"pubdate": pubdate}
		blogTitle = (monthsDictionary[fileName]['title'])
		rssItemTitle = {'title': "<title>" + blogTitle + "</title>"} 
		items[fileName].update(rssItemTitle)
		rssCounter = {"counter": counter}
		items[fileName].update(rssCounter)
		counter += 1
		# constructing the url of the post for the rss feed <link> tag
		itemLink = websiteURL + "/" + year + "/" + monthInNumbers  
		rssItemLink = {'link': "<link>" + itemLink + "</link>"} 
		items[fileName].update(rssItemLink)
		# using the metaDescription for the description of the post 
		# for the rss feed <description> tag
		rssItemDescription = {'description': "<description>" + monthsDictionary[fileName]['metaDescription'] + "</description>"} 
		items[fileName].update(rssItemDescription)
		# using the websiteEmail for the <author> tag of the rss feed
		rssItemAuthor = {'author': "<author>" + websiteEmail + "</author>"} 
		items[fileName].update(rssItemAuthor)
		# using the websiteURL for the <source> tag of the rss feed
		rssItemSource = {'source': "<source>" + websiteURL + "/" +  rssFileName + "</source>"} 
		items[fileName].update(rssItemSource)
		# using the metaTitle for the <category> tag of the rss feed
		rssItemCategory = {'category': "<category>" + monthsDictionary[fileName]['metaTitle'] + "</category>"} 
		items[fileName].update(rssItemCategory)
	return items

def makeRSS(rssDictionary):
	rssList = []
	# build the channel information for the rss feed
	# as defined by https://www.rssboard.org/rss-specification
	# it includes;
	# title - the name of the channel
	# link - the url of website
	# description - a sentence describing the channel  
	# and optional extras include:
	# language - defined here https://www.rssboard.org/rss-language-codes
	# image of the faviconURL	
	# copyright
	# pubDate	The publication date for the content in the channel.
	
	rssBegin = '<?xml version="1.0" encoding="utf-8"?><rss version="2.0">\n'
	rssList.append(rssBegin)
	rssChannelStart = '<channel>\n'
	rssList.append(rssChannelStart)
	rssTitle = '\t<title>' + websiteName + '</title>\n'
	rssList.append(rssTitle)
	rssLink = '\t<link>' + websiteURL + '</link>\n'
	rssList.append(rssLink)
	rssDescription = '\t<description>' + websiteDescription + '</description>\n'
	rssList.append(rssDescription)
	rssLanguage = '\t<language>' + websiteLanguage + '</language>\n'
	rssList.append(rssLanguage)
	rssImage = '\t<image>\n \t\t<title>' + websiteName + '</title>\n \t\t<link>' + websiteURL + '</link>\n \t\t <url>' + faviconURL + '</url>\n \t\t<width>150</width>\n \t\t<height>150</height>\n\t</image>\n' 
	rssList.append(rssImage)

	# identify the pubdate for the latest blog
	# to find this use the rss Dictionary
#	keyForRss = yearDictionary[latestYear]['monthAscending'][0][0]
	latestPostsCounter = []
	# make a list of the counters in the rss entries - they represent order
	# of adding to the rss.csv the greatest being the latest entry 
	for filename in rssDictionary:
		latestPostsCounter.append(rssDictionary[filename]["counter"]) 
	# identify the latest entry to rss.csv from this list of counters
	latestPostsCounter.sort(reverse=True)	
	latestRssItemCounter = latestPostsCounter[0] 
	# find the key value for this lastest entry 
	for filename in rssDictionary:	
		if rssDictionary[filename]['counter'] == latestRssItemCounter:
			keyForRss = filename 	

	latestYear = keyForRss.split('-')

	# pubdate is given in the latest item in the rss.csv 
	current_time = datetime.datetime.now() 
	currentYear = current_time.year
	currentMonth = current_time.month
	rssPubDate = '\t' + rssDictionary[keyForRss]["pubdate"] + '\n'
	rssList.append(rssPubDate)
	rssCopyright = '\t<copyright>Copyright '+ str(currentYear) + ', ' + websiteName +'</copyright>\n'
	rssList.append(rssCopyright)
	# add the items to the rss feed in the order of: 
	# years with most recent year first and 
	# months with most recent month first
	for counter in latestPostsCounter:
		for item in rssDictionary:
			if rssDictionary[item]['counter'] == counter: 
				counterlessItem = dict(rssDictionary[item])
				counterlessItem.pop('counter')
				rssItemStart = '\t\t<item>\n'
				rssList.append(rssItemStart)
				for itemEntry in counterlessItem:
					rssList.append('\t\t\t' + counterlessItem[itemEntry] + '\n')
				rssItemEnd= '\t\t</item>\n'
				rssList.append(rssItemEnd)

	rssChannelEnd = '</channel>\n'
	rssList.append(rssChannelEnd)
	rssEnd = '</rss>\n'
	rssList.append(rssEnd)
	
	# print the entire list out to the rss file
	with open(rssFileName, 'w') as rssFeed:
		for line in rssList:
			rssFeed.write(line)	

def wrapHtml(fileName):
	# a file name is passed in, this file is opened 
	# and read into a list called 'lines'
	# the list entries are wrapped in html paragraph tags based on the
	# ^ begining of line and \n new line characters, marking the begining
	# and end of the paragraph.  
	# and any apostrophes are converted to html &apos
	# and the list is returned. 
	with open(fileName) as file:
		lines = file.readlines()
	for index, line in enumerate(lines):
		lines[index] = re.sub("^", "<p>", line)
	for index, line in enumerate(lines):
		lines[index] = re.sub("\n", "</p>", line)
	for index, line in enumerate(lines):
		lines[index] = re.sub("<p><s>", "<section><p>", line)
	for index, line in enumerate(lines):
		lines[index] = re.sub("</s></p>", "</p></section>", line)
	for index, line in enumerate(lines):
		lines[index] = re.sub("'", "&apos;", line)
	return lines

def makeIndex():
	
	# work out latest year for the link to the notes
	latestYear = yearDescending[0]

	websiteIndex = '\
	<!DOCTYPE html lang="en-GB">\
	<head>\
	<meta charset="utf-8">\
	<title>' + websiteName + '</title>\
	<meta name="author" content="'+ websiteName +'">\
	<meta name="robots" content="index, follow">\
	<meta name="color-scheme" content="dark light">\
	<meta name="viewport" content="width=device-width, initial-scale=1">\
	<link type="text/css" rel="stylesheet" href="'+ styleSheetPathIndex +'">\
	<link rel="icon" type="image/svg" href="' + faviconPathIndex +'">\
	<meta name="viewport"  content="width=device-width, initial-scale=1.0">\
	<meta name="description" content="'+ websiteDescription +'">\
	<meta name="keywords" content="'+ websiteMetaIndex +'">\
	<meta name="copyright" content="'+ websiteName +'">\
	</head>\
	<body>\
	<div class="bodyIndex">\
	<header><h1>'+ websiteName +'</h1></header>\
	<h2>' + websiteDescription + '</h2>\
	<nav class="indexMenu">\
	<a href="' + str(latestYear) +'/index.html"> Notes | </a>\
	<a href="'+ rssFileName +'"> RSS | </a>\
	<a href="about.html"> About </a>\
	</nav>\
	</div>\
	</body>\
	</html>'

	# print the entire list out to the index.html file
	with open("index.html", 'w') as indexFile:
		for line in websiteIndex:
			indexFile.write(line)	

def makeAbout():
	websiteAbout = []
	# create head and append to websiteAbout
	aboutHead = makeHead(styleSheetPathIndex, faviconPathIndex, websiteMetaIndex, websiteDescription)
	websiteAbout.append(aboutHead)
	# create header and navigation and append to websiteAbout
	aboutTitle = '<header><h1>'+ websiteName +'</h1><h2>about</h2></header>'
	websiteAbout.append(aboutTitle)
	aboutNav = '<nav><ol class="breadcrumb"><li><a href="index.html">home</a></li><li>About</li></ol></nav>'
	websiteAbout.append(aboutNav)
	beginMain = '<main>'
	websiteAbout.append(beginMain)

	# open the text file for the about page and wrap it in html 
	# and append to websiteAbout
	print(os.getcwd())
	aboutText = wrapHtml("../about.txt")
	for text in aboutText:
		websiteAbout.append(text)
	# create footer and append to websiteAbout
	endMain = '</main>'
	websiteAbout.append(endMain)
	aboutFooter = makeFooter(rssFileName)
	websiteAbout.append(aboutFooter)	
	
	# print the entire list out to the about.html file
	with open("about.html", 'w') as aboutFile:
		for line in websiteAbout:
			aboutFile.write(line)	

def makeHead(styleSheetPath, faviconPath, metaKeywords, metaDescription):
	header = '<!DOCTYPE html lang="en-GB">\
	<head>\
	<meta charset="utf-8">\
	<title>' + websiteName + '</title>\
	<meta name="author" content="'+ websiteName +'">\
	<meta name="robots" content="index, follow">\
	<meta name="color-scheme" content="light dark">\
	<meta name="viewport" content="width=device-width, initial-scale=1">\
	<link type="text/css" rel="stylesheet" href="'+ styleSheetPath +'">\
	<link rel="icon" type="image/svg" href="' + faviconPath +'">\
	<meta name="viewport"  content="width=device-width, initial-scale=1.0">\
	<meta name="keywords" content="'+ metaKeywords +'">\
	<meta name="description" content="'+ metaDescription +'">\
	<meta name="copyright" content="'+ websiteName +'">\
	</head>\
	<body>'	
	return header

def makeFooter(rssFilePath):
	websiteFooter = '<footer>\
	<p class="footer">' + footerText + 'You can subscribe to the \
	<a href="'+ rssFilePath +'">RSS feed</a> or email at ' + websiteEmail + '</p>\
	</footer>\
	</body>\
	</html>'
	return websiteFooter

def makeItAll():
	# each file in the Blogs directory is a dictionary entry
	# with the key of its filename
	# and values of the month as a number and in word and year 
	monthsDictionary = createDictionaryForMonths()
	yearDictionary = createDictionaryForYears(monthsDictionary)
	rssDictionary = createDictionaryForRSS(monthsDictionary, yearDictionary)
	makeMonth(monthsDictionary)
	makeYear(yearDictionary)
	makeDirectory(yearDictionary, monthsDictionary, rssDictionary)
	#makeSiteMap()

makeItAll()
