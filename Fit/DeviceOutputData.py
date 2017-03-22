#!/usr/bin/env python

#
# copyright Tom Goetz
#

from OutputData import OutputData


class DeviceOutputData(OutputData):

    def __init__(self, file):
        OutputData.__init__(self, file)

    def parse_info(self):
        pass

    def parse_messages(self):
        for device_info_message in self.file['device_info']:
            entry = {}
            entry['file'] = self.file.filename
            for field_name in device_info_message:
                field = device_info_message[field_name]
                entry[field_name] = field['value']
            self.entries.append(entry)

