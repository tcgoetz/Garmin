#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging

from datetime import tzinfo, timedelta, datetime

class MonitoringBData():

    def __init__(self, file):
        self.file = file
        self.headings = ['timestamp', 'activity_type'] 
        self.entries = []

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        self.parse()

    def timestamp16_to_timestamp(self, timestamp_16):
        delta = timestamp_16 - self.matched_timestamp_16
        return self.last_timestamp + timedelta(0, delta)

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

        if units:
            heading = field_name + " (" + units + ")"
        else:
            heading = field_name
        if not heading in self.headings:
            self.headings.append(heading)

    def parse_message(self, message):
        entry = {}

        activity_type_field =  message['activity_type']
        if activity_type_field:
            activity_type_units = activity_type_field['units']
        else:
            activity_type_intensity_field = message['current_activity_type_intensity']
            if activity_type_intensity_field:
                activity_type_units = activity_type_intensity_field['value']['activity_type']['units']
            else:
                activity_type_units = self.activity_type['units'][0]

        for field_name in message:
            field = message[field_name]

            if field_name == 'timestamp':
                self.last_timestamp = field['value']
                self.add_entry_field(entry, field_name, self.last_timestamp)
                self.matched_timestamp_16 = self.last_timestamp_16
            elif field_name == 'timestamp_16':
                timestamp_16_value = field['value']
                self.add_entry_field(entry, 'timestamp', self.timestamp16_to_timestamp(timestamp_16_value))
                self.last_timestamp_16 = timestamp_16_value
            elif field_name == 'cycles':
                self.add_entry_field(entry, activity_type_units, field['value'])
            elif field_name == 'activity_type':
                self.add_entry_field(entry, field_name, field['value'])
            elif field_name == 'current_activity_type_intensity':
                self.add_entry_field(entry, 'activity_type', field['value']['activity_type']['value'])
                self.add_entry_field(entry, 'intensity', field['value']['intensity']['value'])
            else:
                self.add_entry_field(entry, field_name, field['value'], field['units'])

        print(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self):
        messages = self.file['monitoring']

        for message in messages:
            self.entries.append(self.parse_message(message))

    def parse(self):
        self.parse_info()
        self.parse_messages()

    def field_names(self):
        return self.headings

    def fields(self):
        return self.entries

    def __getitem__(self, index):
        return self.entries[index]