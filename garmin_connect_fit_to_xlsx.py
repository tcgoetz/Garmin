#!/usr/bin/env python

#
# copyright Tom Goetz
#

import os, sys, getopt, re, string, logging, datetime

import Fit

from Garmin import GarminXlsxWriter


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GarminFitData():

    def __init__(self, input_file, input_dir, english_units):
        self.fitfiles = []

        if input_file:
            logger.info("Reading file: " + input_file)
            self.fitfiles.append(Fit.File(input_file, english_units))
        if input_dir:
            logger.info("Reading directory: " + input_dir)
            file_names = self.dir_to_fit_files(input_dir)
            for file_name in file_names:
                self.fitfiles.append(Fit.File(file_name, english_units))

        self.headings = None
        self.fields = None

    def dir_to_fit_files(self, input_dir):
        file_names = []

        for file in os.listdir(input_dir):
            match = re.search('.*\.fit', file)
            if match:
                file_names.append(input_dir + "/" + file)

        logger.debug(file_names)

        return file_names

    def write_monitoring(self, gd_xlsx):
        monitoring = Fit.MonitoringOutputData(self.fitfiles)

        gd_xlsx.start_activity('monitoring')
        self.headings = monitoring.heading_names()
        self.fields = monitoring.field_names()
        gd_xlsx.write_headings(self.headings)

        last_day = None
        entries = monitoring.fields()
        for entry in entries:
            day = entry['timestamp'].replace(hour=0, minute=0, second=0, microsecond=0)
            if day != last_day:
                highlight = True
                last_day = day
            else:
                highlight=False
            values = []
            for field in self.fields:
                try:
                    values.append(entry[field])
                except KeyError:
                    values.append('')
            gd_xlsx.write_activity_row(values, highlight)
        gd_xlsx.auto_fit()

        gd_xlsx.start_activity('monitoring summary')
        headings = monitoring.get_summary_headings()
        gd_xlsx.write_headings(headings, 2)
        summary_days = monitoring.get_summary()
        dates = summary_days.keys()
        dates.sort()
        for date in dates:
            summary_day = summary_days[date]
            gd_xlsx.write_summary_row(date, summary_day)
        gd_xlsx.auto_fit()

    def process_files(self, output_file):
        gd_xlsx = GarminXlsxWriter(output_file)

        gd_xlsx.start_activity('device')
        device_data = Fit.DeviceOutputData(self.fitfiles)
        for field in device_data.fields():
            gd_xlsx.write_activity_footer(field)
        gd_xlsx.auto_fit()

        self.write_monitoring(gd_xlsx)

        gd_xlsx.finish()


def usage(program):
    print '%s -o <outputfile> -i <inputfile> ...' % program
    sys.exit()

def main(argv):
    english_units = False
    input_dir = None
    input_file = None
    output_file = ''

    try:
        opts, args = getopt.getopt(argv,"d:ei:o:s:", ["english", "inputfile=","outputfile="])
    except getopt.GetoptError:
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
        elif opt in ("-e", "--english"):
            english_units = True
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

    gd = GarminFitData(input_file, input_dir, english_units)
    gd.process_files(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])