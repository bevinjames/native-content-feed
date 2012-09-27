#! /usr/bin/env python
import time, sys, csv
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from optparse import OptionParser

###################################################################
# Nuts and bolts
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

def formatDate (sDate, sTime):
	# YYYY-MM-DDThh:mm: + ':00+00:00'
	dateList = sDate.split('/')
	return '20' + dateList[2] + '-' + dateList[1] + '-' + dateList[0] + 'T' + sTime + ':00+00:00'

def generateFeed(options):
	# Access files
	clientFile = open(options.input)
	clientProductFeed = open(options.output, 'w')
	dialect = csv.Sniffer().sniff(clientFile.read(1024))
	clientFile.seek(0)
	reader = csv.reader(clientFile, dialect)

	# Define Feed tag values
	generateDateTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
	schemaVersion = 'http://www.bazaarvoice.com/xs/PRR/SyndicationFeed/' + options.schema

	# Build necessary header
	xmlPrefix = '<?xml version="1.0" encoding="UTF-8"?>'
	root = Element('Feed')
	root.set('name', options.clientName)
	root.set('xmlns', schemaVersion)
	root.set('extractDate', generateDateTime)

	i = 0

	# Loop through input
	reader.next() # This starts the iteration at row two, thereby, ignoring the first row with titles
	for line in reader:
		productId = line[0]
		userId = line[1]
		userName = line[2]
		reviewTitle = line[3]
		reviewText = line[4]
		rating = line[5]
		sDate = line[6]
		sTime = line[7]
		submissionTime = formatDate(sDate, sTime)

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







































