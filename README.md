Instructions
============

This script ingests a CSV file and outputs an XML feed that conforms to the BV schema for native content imports.
The XML file can then be used to push content to Bazaarvoice.


Files
-----

Here are the list of files in this directory:

* native_content-rr.csv -- The base CSV file with existing review data.
* native_content-rr.xml -- The output of the CSV file into a Bazaarvoice-specific XML format.
* native_content_feed_generator-rr.py -- The script to transform the data.


Usage
-----

    > python native_content_feed_generator-rr.py -c democlient -i native_content-rr.csv -o native_content-rr.xml -m APPROVED -S 5.1
    > python name_of_script.py -c clientName - i location_of_input_csv -o location_of_output_xml -m moderationStatus (APPROVED or SUBMITTED) -s schemaVersion (optional; defaults to '5.1')
