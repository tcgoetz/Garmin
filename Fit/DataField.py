#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from Data import Data


class DataField(Data):

    def __init__(self, file, definition_message, field_definition):
        self.field_definition = field_definition

        fdn = field_definition.fdn_value()
        self.field = definition_message.field(fdn)

        endian = definition_message.architecture()
        type = field_definition.type_string()
        count = field_definition.type_count()
        schema = collections.OrderedDict( [ (self.field.name, [type, count, '%d']) ] )

        Data.__init__(self, file, schema, None, endian)

    def convert(self):
        self.value_obj = self.field.convert(self[self.field.name], self.field_definition.invalid())

    def name(self):
        return self.value_obj['name']

    def value(self):
        return self.value_obj

    def __iter__(self):
        return iter(self.value_obj)

    def keys(self):
        return self.value_obj.keys()

    def items(self):
        return self.value_obj.items()

    def values(self):
        return self.value_obj.values()

    def __str__(self):
        return str(self.value_obj)

