#!/usr/bin/env python

#
# copyright Tom Goetz
#

import os, sys, getopt, re, string, logging, datetime

import Fit

from Garmin import GarminXlsxWriter


#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


class GarminFitData():

    def __init__(self, input_file, input_dir):
        self.fitfiles = []

        if input_file:
            self.fitfiles.append(Fit.File(input_file))
        if input_dir:
            file_names = self.dir_to_fit_files(input_dir)
            for file_name in file_names:
                self.fitfiles.append(Fit.File(file_name))

        self.headings = None
        self.fields = None

    def dir_to_fit_files(self, input_dir):
        file_names = []

        for file in os.listdir(input_dir):
            match = re.search('.*\.fit', file)
            if match:
                file_names.append(input_dir + "/" + file)

        logging.debug(file_names)

        return file_names

    def write_monitoring(self, fitfile, gd_xlsx):
        monitoring = fitfile.get_monitoring()

        if not self.headings:
            self.headings = monitoring.heading_names()
            self.fields = monitoring.field_names()
            gd_xlsx.write_headings(self.headings)

        entries = monitoring.fields()
        for entry in entries:
            values = []
            for field in self.fields:
                try:
                    values.append(entry[field])
                except KeyError:
                    values.append('')
            gd_xlsx.write_activity_row(values)

    def process_files(self, output_file):
        gd_xlsx = GarminXlsxWriter(output_file)

        gd_xlsx.start_activity('device')
        for fitfile in self.fitfiles:
            device_data = fitfile.get_device()
            gd_xlsx.write_activity_footer(device_data.fields())
        gd_xlsx.auto_fit()

        gd_xlsx.start_activity('monitoring')
        for fitfile in self.fitfiles:
            file_type_field = fitfile.type()
            file_type = file_type_field['value']
            if file_type == 'monitoring_b':
                self.write_monitoring(fitfile, gd_xlsx)

        gd_xlsx.auto_fit()
        gd_xlsx.finish()


def usage(program):
    print '%s -o <outputfile> -i <inputfile> ...' % program
    sys.exit()

def main(argv):
    input_dir = None
    input_file = None
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
        elif opt in ("-d", "--input_dir"):
            input_dir = arg
        elif opt in ("-i", "--inputfile"):
            logging.debug("Input File: %s" % arg)
            input_file = arg
        elif opt in ("-o", "--outputfile"):
            logging.debug("Output file: %s" % arg)
            output_file = arg

    if not (input_file or input_dir) or not output_file:
        print "Missing arguments:"
        usage(sys.argv[0])

    gd = GarminFitData(input_file, input_dir)
    gd.process_files(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])