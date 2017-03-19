#!/usr/bin/env python

#
# copyright Tom Goetz
#

import os, sys, getopt, re, string, logging, datetime

import Fit

from Garmin import GarminXlsxWriter


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


class GarminFitData():

    def __init__(self, input_file):
        self.fitfile = Fit.File(input_file)

    def write_monitoring_b(self, gd_xlsx):
        monitoring = self.fitfile.get_monitoring_b()

        headings = monitoring.field_names()
        gd_xlsx.write_headings(headings)

        entries = monitoring.fields()
        for entry in entries:
            values = []
            for heading in headings:
                try:
                    values.append(entry[heading])
                except KeyError:
                    values.append('')
            gd_xlsx.write_activity_row(values)

    def process_file(self, output_file):
        gd_xlsx = GarminXlsxWriter(output_file)

        file_type_field = self.fitfile.type()
        file_type = file_type_field['value']

        gd_xlsx.start_activity(file_type)

        file_time_created_field = self.fitfile.time_created()

        if file_type == 'monitoring_b':
            self.write_monitoring_b(gd_xlsx)

        gd_xlsx.auto_fit()
        gd_xlsx.finish()


def usage(program):
    print '%s -o <outputfile> -i <inputfile> ...' % program
    sys.exit()

def main(argv):
    input_dir = ''
    output_file = ''
    start_date = None
    days_per_file = 7

    try:
        opts, args = getopt.getopt(argv,"d:i:o:s:", ["inputfile=","outputfile="])
    except getopt.GetoptError:
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
        elif opt in ("-i", "--inputfile"):
            logging.debug("Input File: %s" % arg)
            input_file = arg
        elif opt in ("-o", "--outputfile"):
            logging.debug("Output file: %s" % arg)
            output_file = arg

    if not input_file or not output_file:
        print "Missing arguments:"
        usage(sys.argv[0])

    gd = GarminFitData(input_file)
    gd.process_file(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])