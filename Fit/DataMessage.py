#!/usr/bin/env python

#
# copyright Tom Goetz
#

import collections

from DataField import DataField


class DataMessage():

    def __init__(self, definition_message, file, english_units=False):
        self.definition_message = definition_message

        self.fields = {}
        self.file_size = 0
        self._timestamp = None

        for index in xrange(definition_message.field_count()):
            data_field = DataField(file, definition_message, definition_message.field_definitions[index], english_units)
            self.file_size += data_field.file_size
            self.fields[data_field.name()] = data_field.value()

    def type(self):
        return self.definition_message.message_number()

    def name(self):
        return self.definition_message.name()

    def timestamp(self):
        return self._timestamp

    def __getitem__(self, name):
        try:
            return self.fields[name]
        except KeyError:
            return None

    def __iter__(self):
        return iter(self.fields)

    def keys(self):
        return self.fields.keys()

    def items(self):
        return self.fields.items()

    def values(self):
        return self.fields.values()

    def __str__(self):
        return ("%s: %s (%d)" % (self.__class__.__name__,  self.name(), self.type()))