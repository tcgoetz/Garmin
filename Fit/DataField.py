#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from Data import Data


class DataField(Data):

    def __init__(self, file, definition_message, field_definition):
        fdn = field_definition.fdn_value()
        self.field = definition_message.field(fdn)
        type = field_definition.type_string()
        count = field_definition.type_count()
        schema = collections.OrderedDict( [ (self.field.name, [type, count, '%d']) ] )
        Data.__init__(self, file, schema)

    def value(self):
        return self.decoded_data[self.field.name]

    def __str__(self):
        return self.field.display(self.value())

