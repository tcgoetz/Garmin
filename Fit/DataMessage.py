#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from DataField import DataField


class DataMessage():

    def __init__(self, definition_message, file):
        self.definition_message = definition_message

        self.data_fields = []
        self.file_size = 0
        for index in xrange(definition_message.field_count()):
            data_field = DataField(file, definition_message, definition_message.field_definitions[index])
            self.file_size += data_field.file_size
            self.data_fields.append(data_field)
