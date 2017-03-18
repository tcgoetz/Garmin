#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from DataField import DataField


class DataMessage():

    def __init__(self, definition_message, file):
        self.definition_message = definition_message

        logging.debug(str(self))

        self.data_fields = []
        self.file_size = 0
        for index in xrange(definition_message.field_count()):
            data_field = DataField(file, definition_message, definition_message.field_definitions[index])
            self.file_size += data_field.file_size
            self.data_fields.append(data_field)

    def type(self):
        return self.definition_message.message_number()

    def name(self):
        return self.definition_message.name()

    def field(self, name):
        for data_field in self.data_fields:
            if data_field.name() == name:
                return data_field.value_str()
        return None

    def __str__(self):
        return ("%s: %s (%d)" % (self.__class__.__name__,  self.name(), self.type()))