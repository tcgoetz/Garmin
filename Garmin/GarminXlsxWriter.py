#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, datetime, xlsxwriter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GarminXlsxWriter(object):
    highlight_none          = 1
    highlight_lighter_gray  = 2
    highlight_light_gray    = 3
    highlight_gray          = 4
    highlight_dark_gray     = 5
    highlight_yellow        = 6
    highlight_orange        = 7
    highlight_red           = 8
    highlight_pattern       = 9
    highlight_light_blue    = 10

    def __init__(self, filename):
        logger.info("Creating '%s'..." % filename)
        self.autofit_col_padding = 0
        self.clear_fit_data()
        self.filename = filename
        self.workbook = xlsxwriter.Workbook(self.filename, {'strings_to_numbers': True})
        self.workbook.set_properties({'title' : 'Garmin Connect Data', 'author' : 'garmin_connect_export.py',
                                        'category' : 'Health', 'keywords' : 'Garmin, Connect, Exercise, Health, Data'})
        self.date_format_str = 'mm/dd/yyyy'
        self.date_format = self.workbook.add_format({'num_format': self.date_format_str})
        self.date_time_format_str = 'mm/dd/yyyy hh:mm:ss'
        self.date_time_format = self.workbook.add_format({'num_format': self.date_time_format_str})
        self.heading_format = self.workbook.add_format({'bold': 1})
        self.highlight_white_format = self.workbook.add_format({'bg_color': '#FFFFFF'})
        self.highlight_lighter_gray_format = self.workbook.add_format({'bg_color': '#F8F8F8'})
        self.highlight_light_gray_format = self.workbook.add_format({'bg_color': '#F0F0F0'})
        self.highlight_gray_format = self.workbook.add_format({'bg_color': '#D3D3D3'})
        self.highlight_dark_gray_format = self.workbook.add_format({'bg_color': '#B0B0B0'})
        self.highlight_light_blue_format = self.workbook.add_format({'bg_color': '#99ccff'})
        self.highlight_yellow_format = self.workbook.add_format({'bg_color': '#FFFF00'})
        self.highlight_orange_format = self.workbook.add_format({'bg_color': '#FF6600'})
        self.highlight_red_format = self.workbook.add_format({'bg_color': '#FF0000'})
        self.highlight_pattern_format = self.workbook.add_format({'pattern': 3})
        self.worksheet = None

    def clear_fit_data(self):
        self.col_widths = []
        self.col_count = 0

    def record_data_period(self, start_date, end_date):
        self.workbook.set_custom_property('Data Start Date',  start_date)
        self.workbook.set_custom_property('Data End Date',  end_date)

    def next_row(self):
        self.row += 1

    def column_letter(self, index):
        return chr(ord('A') + index)

    def calculate_fit(self, string, extra_padding=0):
        length = len(string) + self.autofit_col_padding + extra_padding
        while self.col_count < (self.col + 1):
            self.col_widths.append(0)
            self.col_count += 1
        if self.col_widths[self.col] < length:
            self.col_widths[self.col] = length

    def calculate_date_fit(self, date_format):
        self.calculate_fit(date_format)

    def auto_fit(self):
        for index, col_width in enumerate(self.col_widths):
            self.worksheet.set_column(index, index, col_width)

    def write_cell(self, value, format=None):
        logger.debug("Cell (%d, %d) : %s" % (self.row, self.col, value))
        self.worksheet.write(self.row, self.col, value, format)
        self.calculate_fit(str(value))
        self.col += 1

    def write_cell_datetime(self, date):
        self.worksheet.write_datetime(self.row, self.col, date, self.date_time_format)
        self.calculate_date_fit(self.date_time_format_str)
        self.col += 1

    def write_cell_date(self, date):
        if date:
            if date.hour or date.minute or date.second:
                self.worksheet.write_datetime(self.row, self.col, date, self.date_time_format)
                self.calculate_date_fit(self.date_time_format_str)
            else:
                self.worksheet.write_datetime(self.row, self.col, date, self.date_format)
                self.calculate_date_fit(self.date_format_str)
        self.col += 1

    def write_cell_string(self, string, format=None, extra_padding=0):
        self.worksheet.write_string(self.row, self.col, string, format)
        self.calculate_fit(string, extra_padding)
        self.col += 1

    def write_cell_heading(self, heading):
        self.write_cell_string(heading, self.heading_format, 5)

    def highlight_format(self, highlight):
        highlight_values = {
            self.highlight_none         : None, 
            self.highlight_lighter_gray : self.highlight_lighter_gray_format,
            self.highlight_light_gray   : self.highlight_light_gray_format,
            self.highlight_gray         : self.highlight_gray_format,
            self.highlight_dark_gray    : self.highlight_dark_gray_format,
            self.highlight_yellow       : self.highlight_yellow_format,
            self.highlight_orange       : self.highlight_orange_format,
            self.highlight_red          : self.highlight_red_format,
            self.highlight_pattern      : self.highlight_pattern_format,
            self.highlight_light_blue   : self.highlight_light_blue_format
        }
        return highlight_values[highlight]

    def set_highlight_row(self, highlight):
        self.worksheet.set_row(self.row, None, self.highlight_format(highlight))

    def set_highlight_col(self, col, highlight):
        print self.col_widths[col]
        self.worksheet.set_column(col, col, self.col_widths[col], self.highlight_format(highlight))

    def write_highlight_cell(self, value, highlight):
        self.write_cell(value, self.highlight_format(highlight))

    def write_average_row(self, row_start, row_end, avg_cols):
        self.col = 0
        self.write_cell_string("Average", self.heading_format)
        for avg_col in avg_cols:
            col_letter = self.column_letter(avg_col)
            formula = "=AVERAGE(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logger.debug("Average %d : %s" % (avg_col, formula))
            self.worksheet.write_formula(self.row, avg_col, formula)
        self.row += 1

    def write_conditional_avg_row(self, row_start, row_end, conditional_col, condition, col):
        self.col = 0
        self.write_cell_string("Average %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        col_letter = self.column_letter(col)
        formula = '=AVERAGEIF(%c%d:%c%d, "%s", %c%d:%c%d)' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, total_col_letter, row_start + 1, col_letter, row_end + 1)
        logger.debug("AverageCond %d : %s" % (col, formula))
        self.worksheet.write_formula(self.row, col, formula)
        self.row += 1

    def write_total_row(self, row_start, row_end, total_cols):
        self.col = 0
        self.write_cell_string("Total", self.heading_format)
        for total_col in total_cols:
            col_letter = self.column_letter(total_col)
            formula = "=SUM(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logger.debug("Total %d : %s" % (total_col, formula))
            self.worksheet.write_formula(self.row, total_col, formula)
        self.row += 1

    def write_conditional_total_row(self, row_start, row_end, conditional_col, condition, total_col):
        self.col = 0
        self.write_cell_string("Total %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        total_col_letter = self.column_letter(total_col)
        formula = '=SUMIF(%c%d:%c%d, "%s", %c%d:%c%d)' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, total_col_letter, row_start + 1, total_col_letter, row_end + 1)
        logger.debug("TotalCond %d : %s" % (total_col, formula))
        self.worksheet.write_formula(self.row, total_col, formula)
        self.row += 1

    def write_max_row(self, row_start, row_end, max_cols):
        self.col = 0
        self.write_cell_string("Max", self.heading_format)
        for max_col in max_cols:
            col_letter = self.column_letter(max_col)
            formula = "=MAX(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logger.debug("Max %d : %s" % (max_col, formula))
            self.worksheet.write_formula(self.row, max_col, formula)
        self.row += 1

    def write_conditional_max_row(self, row_start, row_end, conditional_col, condition, max_col):
        self.col = 0
        self.write_cell_string("Max %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        max_col_letter = self.column_letter(max_col)
        formula = '{=MAX(IF(%c%d:%c%d="%s",%c%d:%c%d))}' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, max_col_letter, row_start + 1, max_col_letter, row_end +1)
        logger.debug("MaxCond %d : %s" % (max_col, formula))
        self.worksheet.write_formula(self.row, max_col, formula)
        self.row += 1

    def write_min_row(self, row_start, row_end, min_cols):
        self.col = 0
        self.write_cell_string("Min", self.heading_format)
        for min_col in min_cols:
            col_letter = self.column_letter(min_col)
            formula = "=MIN(%c%d:%c%d)" % (col_letter, row_start + 1, col_letter, row_end + 1)
            logger.debug("Min %d : %s" % (min_col, formula))
            self.worksheet.write_formula(self.row, min_col, formula)
        self.row += 1

    def write_conditional_min_row(self, row_start, row_end, conditional_col, condition, min_col):
        self.col = 0
        self.write_cell_string("Min %s" % condition, self.heading_format)
        cond_col_letter = self.column_letter(conditional_col)
        min_col_letter = self.column_letter(min_col)
        formula = '{=MIN(IF(%c%d:%c%d="%s",%c%d:%c%d))}' % \
            (cond_col_letter, row_start + 1, cond_col_letter, row_end + 1, condition, min_col_letter, row_start + 1, min_col_letter, row_end +1)
        logger.debug("MinCond %d : %s" % (min_col, formula))
        self.worksheet.write_formula(self.row, min_col, formula)
        self.row += 1

    def start_activity(self, activity_name):
        logger.info("Writing activity '%s'..." % activity_name)
        self.clear_fit_data()
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
        self.worksheet.freeze_panes(self.row, self.col)

    def write_activity_row(self, values, row_highlight=None, cell_highlights={}):
        self.col = 0
        if row_highlight:
            self.set_highlight_row(row_highlight)
        self.write_cell_datetime(values[0])
        for index in range(1, len(values)):
            if index in cell_highlights.keys():
                cell_highlight = cell_highlights[index]
            else:
                cell_highlight = self.highlight_none
            self.write_highlight_cell(values[index], cell_highlight)
        self.row += 1

    def write_summary_row(self, date, summary_dict, highlight_fields):
        logger.debug("Summary %s : %s" % (str(date), str(summary_dict)))
        field_names = summary_dict.keys()
        self.col = 0
        self.write_cell_date(date)
        self.set_highlight_row(self.highlight_gray)
        for field_name in field_names:
            self.col = 1
            field_value = summary_dict[field_name]
            self.write_cell_heading(field_name)
            for name in field_value.keys():
                if field_name in highlight_fields.keys() and name in highlight_fields[field_name].keys():
                    cell_highlight = highlight_fields[field_name][name]
                else:
                    cell_highlight = self.highlight_none
                self.write_highlight_cell(field_value[name], cell_highlight)
            self.row += 1

    def write_activity_footer(self, values_dict):
        self.row += 1
        for value_name in values_dict:
            logger.debug("Footer %s : %s" % (value_name, str(values_dict[value_name])))
            self.col = 0
            self.write_cell_heading(value_name)
            if value_name == 'timestamp':
                self.write_cell_date(values_dict[value_name])
            else:
                value = values_dict[value_name]
                if isinstance(value, list):
                    for index, sub_value in enumerate(value):
                        self.write_cell(value[index])
                else:
                    self.write_cell(values_dict[value_name])
            self.row += 1

    def start_summary_stats(self):
        logger.info("Writing stats...")
        self.clear_fit_data()
        self.worksheet = self.workbook.add_worksheet('Statistics')

    def write_stats_row(self, activity_type, activity_stats):
        logger.info("Writing stats for '%s'..." % activity_type)
        self.col = 0
        self.write_cell_string(activity_type, self.heading_format)
        for heading in activity_stats:
            if 'date' in heading:
                self.write_cell_date(activity_stats[heading])
            else:
                self.write_cell(activity_stats[heading])
        self.row += 1

    def finish(self):
        logger.info("Finishing %s" % self.filename)
        self.workbook.close()
