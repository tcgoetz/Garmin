#!/usr/bin/env python

import os, sys, getopt, re, string, logging, datetime, xlsxwriter

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


class GarminActivityData():

    def __init__(self, start_date, days_per_file):
        self.title = None
        self.start_date = start_date
        self.days_per_file = days_per_file
        self.file_count = 0
        self.heading_count = 0
        self.values_count = 0
        self.record_count = 0
        self.first_date = None
        self.last_date = None
        self.days = 0
        self.lines = []


    def statistics(self):
        stats = {}

        stats['file_count']     = self.file_count
        stats['heading_count']  = self.heading_count
        stats['values_count']   = self.values_count
        stats['record_count']   = self.record_count
        stats['first_date']     = self.first_date
        stats['last_date']      = self.last_date
        stats['days']           = self.days

        return stats


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


    def day_to_datetime(self, start_date, day):
        day_to_index = { "Mon" : 0, "Tue" : 1, "Wed" : 2, "Thu" : 3, "Fri" : 4, "Sat" : 5, "Sun" : 6}
        day_index = day_to_index[day]
        start_day_index = start_date.weekday()
        delta_days = day_index - start_day_index
        if delta_days < 0:
            delta_days += 7
        return (start_date + datetime.timedelta(days=delta_days))



    def month_day_to_datetime(self, start_date, month_day):
        match = re.search('([JFMASOND]{1}[a-z]{2})\s([0-9]{1,2})', month_day)
        if match:
            month = match.group(1)
            day = match.group(2)

            month_to_index = { "Jan" : 1, "Feb" : 2, "Mar" : 3, "Apr" : 4, "May" : 5, "Jun" : 6, "Jul" : 7,
                            "Aug" : 8, "Sep" : 9, "Oct" : 10, "Nov" : 11, "Dec" : 12}

            month_index = month_to_index[month]
            date_str = "%s-%d-%s" % (start_date.year, month_index, day)
            return (datetime.datetime.strptime(date_str, "%Y-%m-%d"))
        else:
            return None


    def track_dates(self, first_date, last_date, date):
        if first_date is None:
            first_date = date
        elif date < first_date:
            first_date = date
        if last_date is None:
            last_date = date
        elif date > last_date:
            last_date = date
        return (first_date, last_date)


    def import_file(self, filename):
        self.title = None
        self.headings = ['Date']
        self.heading_count = 0

        file_start_date = self.start_date + datetime.timedelta(days=(self.file_count * self.days_per_file))

        logging.info("Opening %d : %s" % (self.file_count, filename))
        with open(filename, "r") as f:
            self.read_title(f.readline())
            self.read_headings(f.readline())

            logging.debug(self.title)
            logging.debug(self.headings)

            file_first_date = None
            file_last_date = None

            for line in f:
                values = self.line_to_values(line)
                self.values_count = len(values)

                if self.values_count != self.heading_count:
                    logging.error("Headings %d != Values %d" % (self.heading_count, self.values_count))

                # rewrite the day column to a datetime
                try:
                    values[0] = self.day_to_datetime(file_start_date, values[0])
                    self.days_per_file = 7
                except:
                    try:
                        values[0] = datetime.datetime.strptime(values[0], "%Y-%m-%d")
                    except:
                        values[0] = self.month_day_to_datetime(file_start_date, values[0])
                logging.debug("Date: %s" % values[0])

                (file_first_date, file_last_date) = self.track_dates(file_first_date, file_last_date, values[0])
                (self.first_date, self.last_date) = self.track_dates(self.first_date, self.last_date, values[0])

                self.record_count += 1
                self.lines.append(values)
        self.file_count += 1
        date_span = file_last_date - file_first_date
        if date_span.days > 7:
            self.days_per_file = 28
        date_span = self.last_date - self.first_date
        self.days = date_span.days


    def import_files(self, input_files):
        for input_file in input_files:
            self.import_file(input_file)


    def write_file(self, workbook):
        worksheet = workbook.add_worksheet(self.title)
        date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})

        # write the column headings
        row = 0;
        col = 0
        logging.debug(self.headings)
        for heading in self.headings:
            worksheet.write_string(row, col, heading)
            col += 1
        row += 1
        col = 0

        self.lines.sort()

        # write the data
        for values in self.lines:
            worksheet.write_datetime(row, col, values[0], date_format)
            col += 1

            logging.debug(values)
            for index in range(1, len(values)):
                worksheet.write(row, col, values[index])
                col += 1
            row += 1
            col = 0

        # write the footer
        row += 1
        worksheet.write_string(row, 0, "Files")
        worksheet.write_number(row, 1, self.file_count)
        row += 1
        worksheet.write_string(row, 0, "Records")
        worksheet.write_number(row, 1, self.record_count)
        row += 1
        worksheet.write_string(row, 0, "Days")
        worksheet.write_number(row, 1, self.days)



class GarminData():

    def __init__(self, input_dir, days_per_file):
        self.days_per_file = days_per_file
        self.file_types = {}
        self.stats = {}
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
        gad = GarminActivityData(start_date, self.days_per_file)
        files = self.file_types[activity_type]
        gad.import_files(files)
        gad.write_file(workbook)
        self.stats[gad.title] = gad.statistics()


    def process_files(self, start_date, output_file):
        workbook = xlsxwriter.Workbook(output_file, {'strings_to_numbers': True})

        for activity_type in self.file_types:
            logging.info("Processing %s..." % (activity_type))
            self.process_file_type(start_date, activity_type, workbook)

        worksheet = workbook.add_worksheet("Statistics")
        date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
        row = 0
        col = 0
        for activity_type in self.stats:
            activity_type_stats = self.stats[activity_type]
            logging.info("Writing stats for %s..." % activity_type)
            if row == 0:
                col = 1
                for heading in activity_type_stats:
                    worksheet.write_string(row, col, heading)
                    col += 1
            row += 1
            worksheet.write_string(row, 0, activity_type)
            col = 1
            for heading in activity_type_stats:
                    if 'date' in heading:
                        worksheet.write_datetime(row, col, activity_type_stats[heading], date_format)
                    else:
                        worksheet.write(row, col, activity_type_stats[heading])
                    col += 1

        logging.info("Finishing %s" % output_file)
        workbook.close()



def usage(program):
    print '%s -d <days> -s <startdate> -o <outputfile> -i <inputfile> -i <inputfile> ...' % program
    sys.exit()

def main(argv):
    input_dir = ''
    output_file = ''
    start_date = None
    days_per_file = 7

    try:
        opts, args = getopt.getopt(argv,"d:i:o:s:", ["days_per_file", "input_dir=","output_file=","start_date"])
    except getopt.GetoptError:
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
        elif opt in ("-d", "--days_per_file"):
            days_per_file = int(arg)
            logging.debug("Days: %d" % days_per_file)
        elif opt in ("-i", "--input_dir"):
            logging.debug("Input Dir: %s" % arg)
            input_dir = arg
        elif opt in ("-o", "--output_file"):
            logging.debug("Output file: %s" % arg)
            output_file = arg
        elif opt in ("-s", "--start_date"):
            logging.debug("Start Date: %s" % arg)
            start_date = datetime.datetime.strptime(arg, "%m/%d/%Y")

    if not input_dir or not output_file or not start_date:
        print "Missing arguments:"
        usage(sys.argv[0])

    gd = GarminData(input_dir, days_per_file)
    gd.process_files(start_date, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])