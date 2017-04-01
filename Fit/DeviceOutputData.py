#!/usr/bin/env python

#
# copyright Tom Goetz
#

from OutputData import OutputData


class DeviceOutputData(OutputData):

    def __init__(self, files):
        OutputData.__init__(self, files)

    def parse_messages(self, file, file_created):
        for device_info_message in file['device_info']:
            entry = {}
            entry['file'] = file.filename
    #        entry['type'] = file.type
            for field_name in device_info_message:
                field_value = device_info_message[field_name]
                if field_value.field.known_field:
                    entry[field_name] = field_value['value']
            self.entries.append(entry)

