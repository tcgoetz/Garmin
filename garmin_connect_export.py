#!/usr/bin/env python

import os, sys, getopt, re, string, logging, datetime, xlsxwriter

logging.basicConfig(level=logging.INFO)


class GarminActivityData():

    def __init__(self, start_date):
        self.start_date = start_date
        self.file_count = 0
        self.lines = []


    def day_to_datetime(self, start_date, day):
        day_to_index = { "Mon" : 0, "Tue" : 1, "Wed" : 2, "Thu" : 3, "Fri" : 4, "Sat" : 5, "Sun" : 6}
        day_index = day_to_index[day]
        start_day_index = start_date.weekday()
        delta_days = day_index - start_day_index
        if delta_days < 0:
            delta_days += 7
        return (start_date + datetime.timedelta(days=delta_days))


    def line_to_values(self, line):
        stripped_line = line.rstrip()
        printable = ''.join([x for x in stripped_line if x in string.printable])
        values = printable.split(",")
        logging.debug(values)
        return (values)


    def read_title(self, line):
        values = self.line_to_values(line)
        self.title = values[0]


    def read_headings(self, line):
        values = self.line_to_values(line)
        for index in range(1, len(values)):
            self.headings.append(values[index])
        self.heading_count = len(self.headings)

    def import_file(self, filename):
        self.title = None
        self.headings = ['Date']
        self.heading_count = 0

        file_start_date = self.start_date + datetime.timedelta(days=(self.file_count * 7))

        logging.info("Opening %d : %s" % (self.file_count, filename))
        with open(filename, "r") as f:
            self.read_title(f.readline())
            self.read_headings(f.readline())

            logging.debug(self.title)
            logging.debug(self.headings)

            for line in f:
                values = self.line_to_values(line)
                values_count = len(values)

                # rewrite the day column to a datetime
                day = values[0]
                try:
                    values[0] = self.day_to_datetime(file_start_date, day)
                except:
                    values[0] = datetime.datetime.strptime(day, "%Y-%m-%d")
                logging.debug("Date: %s" % values[0])

                if values_count != self.heading_count:
                    logging.error("Headings %d != Values %d" % (self.heading_count, values_count))
                self.lines.append(values)
        self.file_count += 1


    def import_files(self, input_files):
        for input_file in input_files:
            self.import_file(input_file)


    def write_file(self, workbook):
        worksheet = workbook.add_worksheet(self.title)
        date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})

        row = 0;
        col = 0
        logging.debug(self.headings)
        for heading in self.headings:
            worksheet.write_string(row, col, heading)
            col += 1
        row += 1
        col = 0

        self.lines.sort()

        for values in self.lines:
            worksheet.write_datetime(row, col, values[0], date_format)
            col += 1

            logging.debug(values)
            for index in range(1, len(values)):
                worksheet.write(row, col, values[index])
                col += 1
            row += 1
            col = 0



class GarminData():

    def __init__(self, input_dir):
        self.file_types = {}
        self.dir_to_activity_files(input_dir)


    def dir_to_activity_files(self, input_dir):
        for file in os.listdir(input_dir):
            match = re.search('([A-Z]+)_([_A-Z]+)*.*\.csv', file)
            if match:
                activity_group = match.group(1)
                activity_type = match.group(2)
                logging.debug("%s - %s - %s" % (file, activity_group, activity_type))
                try:
                    self.file_types[activity_type].append(input_dir + "/" + file)
                except:
                    self.file_types[activity_type] = [input_dir + "/" + file]
        logging.debug(self.file_types)


    def process_file_type(self, start_date, activity_type, workbook):
        logging.debug(self.file_types[activity_type])
        gad = GarminActivityData(start_date)
        files = self.file_types[activity_type]
        gad.import_files(files)
        gad.write_file(workbook)


    def process_files(self, start_date, output_file):
        logging.info("Writing %s" % output_file)
        workbook = xlsxwriter.Workbook(output_file, {'strings_to_numbers': True})
        for activity_type in self.file_types:
            self.process_file_type(start_date, activity_type, workbook)
        workbook.close()



def usage(program):
    print '%s -s <startdate> -o <outputfile> -i <inputfile> -i <inputfile> ...' % program
    sys.exit()

def main(argv):
    input_dir = False
    input_files = []
    output_file = ''
    start_date = None

    try:
        opts, args = getopt.getopt(argv,"d:o:s:", ["input_dir=","output_file=","start_date"])
    except getopt.GetoptError:
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
        elif opt in ("-d", "--input_dir"):
            logging.debug("Input Dir: %s" % arg)
            gd = GarminData(arg)
            input_dir = True
        elif opt in ("-o", "--output_file"):
            logging.debug("Output file: %s" % arg)
            output_file = arg
        elif opt in ("-s", "--start_date"):
            logging.debug("Start Date: %s" % arg)
            start_date = datetime.datetime.strptime(arg, "%m/%d/%Y")

    if not input_dir or not output_file or not start_date:
        print "Missing arguments:"
        usage(sys.argv[0])

    gd.process_files(start_date, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])