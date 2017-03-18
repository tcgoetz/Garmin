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
        type = field_definition.type_string()
        count = field_definition.type_count()
        schema = collections.OrderedDict( [ (self.name(), [type, count, '%d']) ] )

        Data.__init__(self, file, schema)

    def name(self):
        return self.field.name

    def value(self):
        return self.decoded_data[self.field.name]

    def value_str(self):
        return self.field.convert(self.value())

    def __str__(self):
        if self.value() != self.field_definition.invalid():
            return self.field.display(self.value())
        else:
            return self.field.display('invalid')

