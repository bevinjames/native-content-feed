#! /usr/bin/env python
import time, sys, csv
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser
from datetime import date

###################################################################
# Helpful defs
###################################################################
def populateTags(parentTag, tagTitle, tagText):
	node = SubElement(parentTag, tagTitle)
	node.text = tagText

def checkForExistence(line, num, errorMsg):
	try: 
		line[num]
		return True
	except IndexError:
		print errorMsg

def formatDate(sDate):
	# 20YY-MM-DD
	m, d, y = sDate.split('/')
	y = '20' + y
	return date(int(y), int(m), int(d)).isoformat()

def populateCdv(cdvs, line, num, label):	
	if line[num] != '':
		elem = line[num]

		# Need to make this more elegant...
		if label == 'Gender':
			cdvId = line[num].title()
		elif label == 'Age':
			cdvId = inAgeRange(line[num])

		cdv = SubElement(cdvs, 'ContextDataValue')
		cdv.set('id', cdvId)
		populateTags(cdv, 'ExternalId', cdvId)
		populateTags(cdv, 'Label', label)

		cdd = SubElement(cdv, 'ContextDataDimension')
		cdd.set('id', label)
		populateTags(cdd, 'ExternalId', label)
		populateTags(cdd, 'Label', label)

def inAgeRange(age):
	# Need to make this more elegant...
	if int(age) < 18:
		return '17orUnder'
	elif int(age) >= 18 and int(age) < 25:
		return '18to24'
	elif int(age) >= 25 and int(age) < 35:
		return '25to34'
	elif int(age) >= 35 and int(age) < 45:
		return '35to44'
	elif int(age) >= 45 and int(age) < 55:
		return '45to54'
	elif int(age) >= 55 and int(age) < 65:
		return '55to64'
	elif int(age) >= 65:
		return '65orOver'

###################################################################
# Generate Feed
###################################################################
def generateFeed(options):
	# Access files
	clientFile = open(options.input, 'rU')
	clientProductFeed = open(options.output, 'w')
	dialect = csv.Sniffer().sniff(clientFile.read(1024))
	clientFile.seek(0)
	reader = csv.reader(clientFile, dialect)

	# Define Feed tag values
	generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
	schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/StandardClientFeed/' + options.schema

	# Build necessary header
	xmlPrefix = '<?xml version="1.0" encoding="UTF-8"?>'
	root = Element('Feed')
	root.set('name', options.clientName)
	root.set('xmlns', schemaVersion)
	root.set('extractDate', generateDateTime)

	i = 0

	# Loop through input
	reader.next()
	for line in reader:
		productId = line[0]
		userId = line[1]
		userName = line[2]
		reviewTitle = line[3]
		reviewText = line[4]
		rating = line[5]
		sDate = line[6]
		sTime = line[7]

		fDate = formatDate(sDate)
		submissionTime = fDate + 'T' + sTime + ':00+00:00'

		i = i + 1
		
		# Product element
		product = SubElement(root, 'Product')
		product.set('id', productId)
		populateTags(product, 'ExternalId', productId)

		# Reviews and review elements
		reviews = SubElement(product, 'Reviews')
		review = SubElement(reviews, 'Review')
		review.set('id', str(i))
		review.set('removed', 'false')

		# Moderation
		populateTags(review, 'ModerationStatus', options.moderation)

		# User info
		userProfile = SubElement(review, 'UserProfileReference')
		userProfile.set('id', userId)
		populateTags(userProfile, 'ExternalId', userId)
		populateTags(userProfile, 'DisplayName', userName)
		populateTags(userProfile, 'Anonymous', 'false')
		populateTags(userProfile, 'HyperlinkingEnabled', 'false')

		# Review content
		populateTags(review, 'Title', reviewTitle)
		populateTags(review, 'ReviewText', reviewText)
		populateTags(review, 'Rating', rating)
		populateTags(review, 'SubmissionTime', submissionTime)

		# Context Data values
		cdvs = SubElement(review, 'ContextDataValues')

		# Context Data value - Age
		if checkForExistence(line, 8, 'User age information is missing'):
			populateCdv(cdvs, line, 8, 'Age')

		# User Location
		if checkForExistence(line, 9, 'User location is missing'):
			if line[9] != '':
				populateTags(review, 'ReviewerLocation', line[9])

		# Context Data value - Gender
		if checkForExistence(line, 10, 'User gender information is missing'):
			populateCdv(cdvs, line, 10, 'Gender')


	clientProductFeed.write(xmlPrefix)
	clientProductFeed.write(tostring(root))

###################################################################
# Handle command line args
###################################################################

def main(argv):
	usage = 'usage: %prog [options] arg'
	parser = OptionParser(usage)
	parser.add_option('-c', '--clientName', help='Database name for the client', action='store', dest='clientName')
	parser.add_option('-i', '--input', help='Location of the CSV input file', action='store', dest='input')
	parser.add_option('-o', '--output', help='Location of the XML output file', action='store', dest='output')
	parser.add_option('-s', '--schema', default='5.1', help='The Bazaarvoice XML schema version', action='store', dest='schema')
	parser.add_option('-m', '--moderation', default='SUBMITTED', help='The moderation status: SUBMITTED OR APPROVED', action='store', dest='moderation')
	
	(options, args) = parser.parse_args()

	generateFeed(options)

if __name__ == "__main__":
    main(sys.argv[1:])	




