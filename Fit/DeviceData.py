#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging


class DeviceData():

    def __init__(self, file):
        self.file = file
        self.entries = {}

        self.parse()

    def parse_info(self):
        device_info_messages = self.file['device_info']

        for device_info_message in device_info_messages:
            for field_name in device_info_message:
                field = device_info_message[field_name]

                self.entries[field_name] = field['value']

    def parse(self):
        self.parse_info()

    def fields(self):
        return self.entries

    def __getitem__(self, key):
        return self.entries[key]