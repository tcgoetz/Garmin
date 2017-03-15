#!/usr/bin/env python

import os, sys, getopt, re, string, logging, datetime, xlsxwriter

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


class GarminDataXlsx():

    def __init__(self, filename):
        self.autofit_col_padding = 1
        self.col_count = 0
        self.col_widths = []
        self.filename = filename
        self.workbook = xlsxwriter.Workbook(self.filename, {'strings_to_numbers': True})
        self.date_format_str = 'mm/dd/yyyy'
        self.date_format = self.workbook.add_format({'num_format': self.date_format_str})
        self.heading_format = self.workbook.add_format({'bold': 1})
        self.worksheet = None


    def next_row(self):
        self.row += 1


    def column_letter(self, index):
        return chr(ord('A') + index)


    def calculate_fit(self, string):
        length = len(string) + self.autofit_col_padding
        if self.col >= self.col_count:
            self.col_widths.append(length)
            self.col_count += 1
        elif self.col_widths[self.col] < length:
            self.col_widths[self.col] = length


    def calculate_date_fit(self):
        self.calculate_fit(self.date_format_str)


    def auto_fit(self):
        for index, col_width in enumerate(self.col_widths):
            self.worksheet.set_column(index, index, col_width)


    def write_cell(self, value, format=None):
        logging.debug("Cell (%d, %d) : %s" % (self.row, self.col, value))
        self.worksheet.write(self.row, self.col, value, format)
        self.calculate_fit(str(value))
        self.col += 1


    def write_cell_date(self, date):
        self.worksheet.write_datetime(self.row, self.col, date, self.date_format)
        self.calculate_date_fit()
        self.col += 1


    def write_cell_string(self, string, format=None):
        self.worksheet.write_string(self.row, self.col, string, format)
        self.calculate_fit(string)
        self.col += 1


    def write_cell_heading(self, heading):
        self.write_cell_string(heading, self.heading_format)


    def write_average_row(self, row_start, row_end, avg_cols):
        self.col = 0
        self.write_cell_string("Average", self.heading_format)
        for avg_col in avg_cols:
            col_letter = self.column_letter(avg_col)
            formula = "=AVERAGE(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logging.debug("Average %d : %s" % (avg_col, formula))
            self.worksheet.write_formula(self.row, avg_col, formula)
        self.row += 1


    def write_conditional_avg_row(self, row_start, row_end, conditional_col, condition, col):
        self.col = 0
        self.write_cell_string("Average %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        col_letter = self.column_letter(col)
        formula = '=AVERAGEIF(%c%d:%c%d, "%s", %c%d:%c%d)' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, total_col_letter, row_start + 1, col_letter, row_end + 1)
        logging.debug("AverageCond %d : %s" % (col, formula))
        self.worksheet.write_formula(self.row, col, formula)
        self.row += 1


    def write_total_row(self, row_start, row_end, total_cols):
        self.col = 0
        self.write_cell_string("Total", self.heading_format)
        for total_col in total_cols:
            col_letter = self.column_letter(total_col)
            formula = "=SUM(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logging.debug("Total %d : %s" % (total_col, formula))
            self.worksheet.write_formula(self.row, total_col, formula)
        self.row += 1


    def write_conditional_total_row(self, row_start, row_end, conditional_col, condition, total_col):
        self.col = 0
        self.write_cell_string("Total %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        total_col_letter = self.column_letter(total_col)
        formula = '=SUMIF(%c%d:%c%d, "%s", %c%d:%c%d)' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, total_col_letter, row_start + 1, total_col_letter, row_end + 1)
        logging.debug("TotalCond %d : %s" % (total_col, formula))
        self.worksheet.write_formula(self.row, total_col, formula)
        self.row += 1


    def write_max_row(self, row_start, row_end, max_cols):
        self.col = 0
        self.write_cell_string("Max", self.heading_format)
        for max_col in max_cols:
            col_letter = self.column_letter(max_col)
            formula = "=MAX(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logging.debug("Max %d : %s" % (max_col, formula))
            self.worksheet.write_formula(self.row, max_col, formula)
        self.row += 1


    def write_conditional_max_row(self, row_start, row_end, conditional_col, condition, max_col):
        self.col = 0
        self.write_cell_string("Max %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        max_col_letter = self.column_letter(max_col)
        formula = '{=MAX(IF(%c%d:%c%d="%s",%c%d:%c%d))}' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, max_col_letter, row_start + 1, max_col_letter, row_end +1)
        logging.debug("MaxCond %d : %s" % (max_col, formula))
        self.worksheet.write_formula(self.row, max_col, formula)
        self.row += 1


    def write_min_row(self, row_start, row_end, min_cols):
        self.col = 0
        self.write_cell_string("Min", self.heading_format)
        for min_col in min_cols:
            col_letter = self.column_letter(min_col)
            formula = "=MIN(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logging.debug("Min %d : %s" % (min_col, formula))
            self.worksheet.write_formula(self.row, min_col, formula)
        self.row += 1


    def write_conditional_min_row(self, row_start, row_end, conditional_col, condition, min_col):
        self.col = 0
        self.write_cell_string("Min %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        min_col_letter = self.column_letter(min_col)
        formula = '{=MIN(IF(%c%d:%c%d="%s",%c%d:%c%d))}' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, min_col_letter, row_start + 1, min_col_letter, row_end +1)
        logging.debug("MinCond %d : %s" % (min_col, formula))
        self.worksheet.write_formula(self.row, min_col, formula)
        self.row += 1


    def start_activity(self, activity_name):
        logging.info("Writing activity '%s'..." % activity_name)
        self.row = 0
        self.col = 0
        self.worksheet = self.workbook.add_worksheet(activity_name)


    def write_headings(self, headings, start_col=0):
        self.row = 0
        self.col = start_col
        for heading in headings:
            self.write_cell_heading(heading)
        self.row = 1
        self.col = 0


    def write_activity_row(self, values):
        self.col = 0
        self.write_cell_date(values[0])

        logging.debug(values)
        for index in range(1, len(values)):
            self.write_cell(values[index])
        self.row += 1


    def write_activity_footer(self, values_dict):
        self.row += 1
        for value_name in values_dict:
            logging.debug("Footer %s : %d" % (value_name, values_dict[value_name]))
            self.col = 0
            self.write_cell_heading(value_name)
            self.worksheet.write_number(self.row, 1, values_dict[value_name])
            self.row += 1


    def start_summary_stats(self):
        logging.info("Writing stats...")
        self.worksheet = self.workbook.add_worksheet('Statistics')


    def write_stats_row(self, activity_type, activity_stats):
        logging.info("Writing stats for '%s'..." % activity_type)
        self.col = 0
        self.write_cell_string(activity_type, self.heading_format)
        for heading in activity_stats:
            if 'date' in heading:
                self.write_cell_date(activity_stats[heading])
            else:
                self.write_cell(activity_stats[heading])
        self.row += 1


    def finish(self):
        logging.info("Finishing %s" % self.filename)
        self.workbook.close()



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


    def activity_attr(self, activity_type, attr_name):
        activity_types = {
                'Active Calories' : { 'total_col' : [2], 'total_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ],
                    'min_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ], 'max_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ] },
                'Average Heart Rate' : { 'avg_cols' : [1] },
                'Calories Consumed' : { 'avg_cols' : [1], 'total_col' : [1], 'max_cols' : [1], 'min_cols' : [1] },
                'Floors Climbed' : { 'avg_cols'  : [1, 3], 'total_col' : [1, 3], 'max_cols' : [1, 3], 'min_cols' : [1, 3] },
                'Intensity Minutes' : { 'avg_cols'  : [1], 'total_col' : [1], 'max_cols' : [1], 'min_cols' : [1] },
                'Max Heart Rate' : { 'avg_cols'  : [1], 'total_col' : [], 'max_cols' : [1], 'min_cols' : [1] },
                'Resting Heart Rate' : { 'avg_cols'  : [1], 'total_col' : [], 'max_cols' : [1], 'min_cols' : [1] },
                'Sleep Time' : { 'avg_cols'  : [1], 'total_col' : [1] },
                'Steps' : { 'avg_cols'  : [1], 'total_col' : [1] },
                'Total Calories' : { 'total_col' : [2], 'total_cond' : [ 1, 2, [ 'Active', 'BMR' ] ], 'min_cond' : [ 1, 2, [ 'Active', 'BMR' ] ],
                    'max_cond' : [ 1, 2, [ 'Active', 'BMR' ] ] },
                'Total Distance' : { 'total_col' : [2], 'total_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ],
                    'min_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ], 'max_cond' : [ 1, 2, [ 'Walking', 'Hiking', 'Running' ] ] },
            }
        try:
            attr = (activity_types[activity_type])[attr_name]
        except:
            attr = None
        return (attr)


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


    def write_summary(self, function, activity_type, attr_name):
        cols = self.activity_attr(self.title, attr_name)
        if cols:
            function(1, self.record_count, cols)


    def write_conditional_summary(self, function, activity_type, condition_name):
        conditions = self.activity_attr(activity_type, condition_name)
        if conditions:
            conditional_col = conditions[0]
            col = conditions[1]
            condition_strings = conditions[2]
            for condition_string in condition_strings:
                function(1, self.record_count, conditional_col, condition_string, col)
            return True
        return False


    def write_file(self, gd_xlsx):
        gd_xlsx.start_activity(self.title)

        # write the column headings
        gd_xlsx.write_headings(self.headings)

        self.lines.sort()

        # write the data
        for values in self.lines:
            gd_xlsx.write_activity_row(values)

        gd_xlsx.next_row()
        self.write_summary(gd_xlsx.write_min_row, self.title, 'min_cols')
        self.write_summary(gd_xlsx.write_max_row, self.title, 'max_cols')
        self.write_summary(gd_xlsx.write_average_row, self.title, 'avg_cols')
        self.write_summary(gd_xlsx.write_total_row, self.title, 'total_col')

        gd_xlsx.next_row()
        if self.write_conditional_summary(gd_xlsx.write_conditional_min_row, self.title, 'min_cond'):
            gd_xlsx.next_row()
        if self.write_conditional_summary(gd_xlsx.write_conditional_max_row, self.title, 'max_cond'):
            gd_xlsx.next_row()
        if self.write_conditional_summary(gd_xlsx.write_conditional_avg_row, self.title, 'avg_cond'):
            gd_xlsx.next_row()
        self.write_conditional_summary(gd_xlsx.write_conditional_total_row, self.title, 'total_cond')

        gd_xlsx.write_activity_footer({"Files" : self.file_count, "Records" : self.record_count, "Days" : self.days})
        gd_xlsx.auto_fit()



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


    def process_file_type(self, start_date, activity_type, gd_xlsx):
        logging.info("Processing %s..." % (activity_type))
        gad = GarminActivityData(start_date, self.days_per_file)
        files = self.file_types[activity_type]
        gad.import_files(files)
        gad.write_file(gd_xlsx)
        self.stats[gad.title] = gad.statistics()


    def process_files(self, start_date, output_file):
        gd_xlsx = GarminDataXlsx(output_file)

        for activity_type in self.file_types:
            self.process_file_type(start_date, activity_type, gd_xlsx)

        # add a sheet with summary stats
        gd_xlsx.start_summary_stats()
 
        for index, activity_type in enumerate(self.stats):
            if index == 0:
                gd_xlsx.write_headings(self.stats[activity_type], 1)
            gd_xlsx.write_stats_row(activity_type, self.stats[activity_type])

        gd_xlsx.auto_fit()
        gd_xlsx.finish()



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