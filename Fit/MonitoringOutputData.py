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
    def __init__(self, file):
        self.heading_names_list = ['timestamp', 'activity_type'] 
        self.field_names_list = ['timestamp', 'activity_type'] 

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        OutputData.__init__(self, file)

    def parse_info(self):
        monitoring_info = self.file['monitoring_info'][0]

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
            elif field_name == 'cycles':
                self.add_entry_field(entry, activity_type_units, field['value'])
            elif field_name == 'activity_type':
                self.add_entry_field(entry, field_name, field['value'])
            elif field_name == 'current_activity_type_intensity':
                self.add_entry_field(entry, 'activity_type', field['activity_type']['value'])
                self.add_entry_field(entry, 'intensity', field['intensity']['value'])
            else:
                self.add_entry_field(entry, field_name, field['value'], field.units())

        logger.debug(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self):
        for message in self.file['monitoring']:
            self.entries.append(self.parse_message(message))

    def field_names(self):
        return self.field_names_list

    def heading_names(self):
        return self.heading_names_list
