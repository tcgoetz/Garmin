#!/usr/bin/env python

#
# copyright Tom Goetz
#

from OutputData import OutputData


class DeviceOutputData(OutputData):

    def __init__(self, files):
        OutputData.__init__(self, files)

    def parse_messages(self, file):
        for device_info_message in file['device_info']:
            entry = {}
            entry['file'] = file.filename
            for field_name in device_info_message:
                field = device_info_message[field_name]
                entry[field_name] = field['value']
            self.entries.append(entry)

