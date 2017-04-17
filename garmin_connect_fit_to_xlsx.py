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

    def dir_to_fit_files(self, input_dir):
        file_names = []

        for file in os.listdir(input_dir):
            match = re.search('.*\.fit', file)
            if match:
                file_names.append(input_dir + "/" + file)

        logger.debug(file_names)

        return file_names

    def fit_file_count(self):
        return len(self.fitfiles)

    def intensity_to_highlight(self, intensity):
        intensity_to_highlight = {
            0 : GarminXlsxWriter.highlight_light_blue, 1 : GarminXlsxWriter.highlight_none,
            2 : GarminXlsxWriter.highlight_none, 3 : GarminXlsxWriter.highlight_yellow,
            4 : GarminXlsxWriter.highlight_yellow, 5 : GarminXlsxWriter.highlight_orange,
            6 : GarminXlsxWriter.highlight_red, 7 : GarminXlsxWriter.highlight_red
        }
        return intensity_to_highlight[intensity]

    def floors_to_highlight(self, height):
        floors = int(height / 13)
        if floors < 10:
            highlight = GarminXlsxWriter.highlight_none
        elif floors < 20:
            highlight = GarminXlsxWriter.highlight_yellow
        elif floors < 30:
            highlight = GarminXlsxWriter.highlight_orange
        else:
            highlight = GarminXlsxWriter.highlight_red
        return highlight

    def set_sleep_period(self, sleep_period):
        self.sleep_period = sleep_period

    def set_hr_zones(self, hr_zones):
        self.hr_zones = hr_zones

    def hr_to_zone(self, hr):
        for index, hr_zone in enumerate(self.hr_zones):
            if hr < hr_zone['max']:
                return index
        return 0

    def hr_to_highlight(self, hr):
        hr_zone_to_highlight = {
            0 : GarminXlsxWriter.highlight_light_blue, 1 : GarminXlsxWriter.highlight_none,
            2 : GarminXlsxWriter.highlight_none, 3 : GarminXlsxWriter.highlight_yellow,
            4 : GarminXlsxWriter.highlight_orange, 5 : GarminXlsxWriter.highlight_red,
        }
        return hr_zone_to_highlight[self.hr_to_zone(hr)]

    def steps_to_highlight(self, steps):
        steps_goal = 10000.0
        if steps > (2 * steps_goal):
            highlight = GarminXlsxWriter.highlight_red
        elif steps > (1.5 * steps_goal):
            highlight = GarminXlsxWriter.highlight_orange
        elif steps > steps_goal:
            highlight = GarminXlsxWriter.highlight_yellow
        elif steps < (0.25 * steps_goal):
            highlight = GarminXlsxWriter.highlight_light_blue
        else:
            highlight = GarminXlsxWriter.highlight_none
        return highlight

    def highlight_from_field(self, field_name, field_value):
        if field_value == '':
            highlight = GarminXlsxWriter.highlight_none
        elif field_name == 'intensity':
            highlight = self.intensity_to_highlight(field_value)
        elif field_name == 'moderate_activity':
            highlight = GarminXlsxWriter.highlight_yellow
        elif field_name == 'vigorous_activity':
            highlight = GarminXlsxWriter.highlight_orange
        elif field_name == 'cum_ascent' or field_name == 'cum_descent':
            highlight = self.floors_to_highlight(field_value)
        elif 'heart_rate' in field_name:
            highlight = self.hr_to_highlight(field_value)
        elif 'steps' in field_name:
            highlight = self.hr_to_highlight(field_value)
        else:
            highlight = GarminXlsxWriter.highlight_none
        return highlight

    def start_worksheet(self, gd_xlsx, title):
        self.last_day = None
        self.last_hour = None
        gd_xlsx.start_activity(title)

    def write_monitoring_period(self, gd_xlsx, title, headings, period_stats, highlight_fields):
        self.start_worksheet(gd_xlsx, title)
        gd_xlsx.write_headings(headings, 2)

        periods = period_stats.keys()
        periods.sort()
        for period in periods:
            gd_xlsx.write_summary_row(period, period_stats[period], highlight_fields)
        logger.info("Wrote %d entries" % len(periods))

        gd_xlsx.auto_fit()
        for index in range(2, len(headings) + 2):
            if (index % 2) == 0:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_lighter_gray)
            else:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_light_gray)

    def write_activity_row(self, gd_xlsx, field_names, entry, hourly_highlight=False):
        day = entry['timestamp'].day
        hour = entry['timestamp'].hour
        if day != self.last_day:
            row_highlight = GarminXlsxWriter.highlight_dark_gray
            self.last_day = day
            self.last_hour = hour
        elif hourly_highlight and (hour != self.last_hour):
            row_highlight = GarminXlsxWriter.highlight_gray
            self.last_hour = hour
        else:
            row_highlight = GarminXlsxWriter.highlight_none

        values = []
        cell_highlights = {}
        for index, field_name in enumerate(field_names):
            if field_name in entry.keys():
                field_value = entry[field_name]
            else:
                field_value = ''

            cell_highlights[index] = self.highlight_from_field(field_name, field_value)
            values.append(field_value)
        gd_xlsx.write_activity_row(values, row_highlight, cell_highlights)

    def write_monitoring_info(self, gd_xlsx):
        monitoring_info = Fit.MonitoringInfoOutputData(self.fitfiles)

        self.start_worksheet(gd_xlsx, 'monitoring info')

        field_names = monitoring_info.field_names()
        gd_xlsx.write_headings(field_names)

        for field in monitoring_info.fields():
            self.write_activity_row(gd_xlsx, field_names, field)
        gd_xlsx.auto_fit()

    def write_monitoring(self, gd_xlsx):
        self.start_worksheet(gd_xlsx, 'monitoring')
        monitoring = Fit.MonitoringOutputData(self.fitfiles, self.sleep_period)

        (first_day, last_day) = monitoring.get_date_span()
        logger.info("Writing date range %s - %s" % (str(first_day), str(last_day)))
        gd_xlsx.record_data_period(first_day, last_day)

        headings = monitoring.heading_names()
        field_names = monitoring.field_names()
        gd_xlsx.write_headings(headings)

        entries = monitoring.fields()
        for entry in entries:
            self.write_activity_row(gd_xlsx, field_names, entry, True)
        logger.info("Wrote %d entries" % len(entries))

        gd_xlsx.auto_fit()
        for index in range(1, len(headings)):
            if (index % 2) == 0:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_lighter_gray)
            else:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_light_gray)

        hourly_highlight_fields = {
            'total_steps' : {'total' : GarminXlsxWriter.highlight_yellow},
            'ascent_floors' : {'total' : GarminXlsxWriter.highlight_yellow},
            'heart_rate' : {
                'avg' : GarminXlsxWriter.highlight_yellow,
                'min' : GarminXlsxWriter.highlight_yellow,
                'max' : GarminXlsxWriter.highlight_yellow
            },
            'intensity' : {'avg' : GarminXlsxWriter.highlight_light_blue},
            'intensity_mins' : {'total' : GarminXlsxWriter.highlight_yellow},
            'resting_heart_rate' : {'avg' : GarminXlsxWriter.highlight_orange}
        }
        self.write_monitoring_period(gd_xlsx, 'monitoring hourly summaries', monitoring.get_stats_headings(),
                                        monitoring.get_hourly_stats(), hourly_highlight_fields)

        daily_highlight_fields = {
            'total_steps' : {'total' : GarminXlsxWriter.highlight_yellow},
            'total_floors' : {'total' : GarminXlsxWriter.highlight_yellow},
            'heart_rate' : {
                'avg' : GarminXlsxWriter.highlight_yellow,
                'min' : GarminXlsxWriter.highlight_yellow,
                'max' : GarminXlsxWriter.highlight_yellow
            },
            'intensity_mins' : {'total' : GarminXlsxWriter.highlight_yellow},
            'resting_heart_rate' : {'min' : GarminXlsxWriter.highlight_yellow}
        }
        self.write_monitoring_period(gd_xlsx, 'monitoring daily summaries', monitoring.get_stats_headings(),
                                        monitoring.get_daily_stats(), daily_highlight_fields)

        self.start_worksheet(gd_xlsx, 'monitoring summary')
        headings = monitoring.get_stats_headings()
        gd_xlsx.write_headings(headings, 2)

        highlight_fields = {
            'intensity_mins' : {'avg' : GarminXlsxWriter.highlight_yellow},
            'total_steps' : {'avg' : GarminXlsxWriter.highlight_yellow},
            'total_floors' : {'avg' : GarminXlsxWriter.highlight_yellow},
            'heart_rate' : {
                'avg' : GarminXlsxWriter.highlight_yellow,
                'min' : GarminXlsxWriter.highlight_yellow,
                'max' : GarminXlsxWriter.highlight_yellow
            },
            'resting_heart_rate' : {
                'min' : GarminXlsxWriter.highlight_yellow,
            }
        }
        overall_stats = monitoring.get_overall_stats()
        gd_xlsx.write_summary_row(monitoring.last_timestamp, overall_stats, highlight_fields)

        gd_xlsx.auto_fit()
        for index in range(2, len(headings) + 2):
            if (index % 2) == 0:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_lighter_gray)
            else:
                gd_xlsx.set_highlight_col(index, GarminXlsxWriter.highlight_light_gray)

    def write_device_data(self, gd_xlsx):
        self.start_worksheet(gd_xlsx, 'device')
        device_data = Fit.DeviceOutputData(self.fitfiles)

        field_names = device_data.field_names()
        gd_xlsx.write_headings(field_names)

        for field in device_data.fields():
            self.write_activity_row(gd_xlsx, field_names, field)
        gd_xlsx.auto_fit()

    def process_files(self, output_file):
        gd_xlsx = GarminXlsxWriter(output_file)

        self.write_device_data(gd_xlsx)
        self.write_monitoring_info(gd_xlsx)
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
    hr_zones = [
        {'min' : 0, 'max' : 85},
        {'min' : 86, 'max' : 102},
        {'min' : 103, 'max' : 119},
        {'min' : 120, 'max' : 137},
        {'min' : 138, 'max' : 154},
        {'min' : 155, 'max' : 250},
    ]
    sleep = {'start' : 22, 'end' : 6}

    try:
        opts, args = getopt.getopt(argv,"d:ei:o:s:z:", ["english", "inputfile=","outputfile=","hrzones"])
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
        elif opt in ("-s", "--sleep"):
            logging.debug("Sleep: %s" % arg)
            sleep_values = arg.split(",")
            sleep = {'start' : sleep_values[0], 'end' : sleep_values[1]}
        elif opt in ("-z", "--hrzones"):
            logging.debug("HR zones : %s" % arg)
            hr_values = arg.split(",")
            next_min = 0
            for count, value in enumerate(hr_values):
                value_int = int(value)
                hr_zones[count]['min'] = next_min
                hr_zones[count]['max'] = value_int
                next_min = value_int + 1

    if not (input_file or input_dir) or not output_file:
        print "Missing arguments:"
        usage(sys.argv[0])

    gd = GarminFitData(input_file, input_dir, english_units)
    gd.set_hr_zones(hr_zones)
    gd.set_sleep_period(sleep)
    if gd.fit_file_count() > 0:
        gd.process_files(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])