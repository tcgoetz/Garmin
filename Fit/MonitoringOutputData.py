#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging
from datetime import tzinfo, timedelta, datetime

from OutputData import OutputData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MonitoringOutputData(OutputData):
    track_max = [ 'cum_active_time' ]
    def __init__(self, files):
        self.heading_names_list = ['timestamp', 'activity_type'] 
        self.field_names_list = ['timestamp', 'activity_type'] 

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        OutputData.__init__(self, files)
        self.parse_summaries()

    def parse_info(self, file):
        monitoring_info = file['monitoring_info'][0]

        self.local_timestamp = monitoring_info['local_timestamp']['value']
        self.last_timestamp = self.local_timestamp
        self.activity_type = monitoring_info['activity_type']
        self.resting_metabolic_rate = monitoring_info['resting_metabolic_rate']
        self.cycles_to_distance = monitoring_info['cycles_to_distance']
        self.cycles_to_calories = monitoring_info['cycles_to_calories']

    def add_entry_field(self, entry, field_name, field_value, units=None):
        entry[field_name] = field_value

        if not field_name in self.field_names_list:
            logger.debug(field_name + ": " + str(units))
            self.field_names_list.append(field_name)
            if units:
                heading = field_name + " (" + units + ")"
            else:
                heading = field_name
            self.heading_names_list.append(heading)

    def parse_message(self, message):
        entry = {}

        activity_type_field =  message['activity_type']
        if activity_type_field:
            activity_type_units = activity_type_field.units()
        else:
            activity_type_intensity_field = message['current_activity_type_intensity']
            if activity_type_intensity_field:
                activity_type_units = activity_type_intensity_field['activity_type'].units()
            else:
                activity_type_units = self.activity_type.units()[0]

        for field_name in message:
            field = message[field_name]

            if field_name == 'timestamp' or field_name == 'timestamp_16':
                self.add_entry_field(entry, 'timestamp', message.timestamp())
            else:
                self.add_entry_field(entry, field_name, field['value'], field.units())

        logger.debug(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self, file):
        self.parse_info(file)
        for message in file['monitoring']:
            self.entries.append(self.parse_message(message))

    def field_names(self):
        return self.field_names_list

    def heading_names(self):
        return self.heading_names_list

    def concatenate_fields(self, first_field, second_field):
        new_field = first_field

        if first_field['min'] > second_field['min']:
            new_field['min'] = second_field['min']
        else:
            new_field['min'] = first_field['min']
        if first_field['max'] < second_field['max']:
            new_field['max'] = second_field['max']
        else:
            new_field['max'] = first_field['max']
        new_field['total'] = first_field['total'] + second_field['total']
        new_field['count'] = first_field['count'] + second_field['count']
        new_field['avg'] = new_field['total'] / new_field['count']

        return new_field

    def concatenate_days(self, first_day, second_day):
        new_day = first_day

        for field_name in second_day:
            second_day_field = second_day[field_name]
            if field_name in first_day:
                first_day_field = first_day[field_name]
                if first_day_field['count'] == 0:
                    new_day[field_name] = second_day_field.copy()
                elif second_day_field['count'] == 0:
                    new_day[field_name] = first_day_field.copy()
                else:
                    new_day[field_name] = self.concatenate_fields(first_day_field, second_day_field)
            # field_name is not in the first day
            else:
                new_day[field_name] = second_day_field.copy()

        return new_day

    def parse_summaries(self):
        self.summary_headings = None
        self.summary_days = {}

        for file in self.files:
            if not self.summary_headings:
                self.summary_headings = file.get_summary_headings()
            new_days = file.get_summary()
            for date in new_days:
                # is the day already in the summary?
                if date in self.summary_days:
                    self.summary_days[date] = self.concatenate_days(self.summary_days[date], new_days[date])
                # date is not in the summary
                else:
                    self.summary_days[date] = new_days[date].copy()

    def get_summary_headings(self):
        return self.summary_headings

    def get_summary(self):
        return self.summary_days
