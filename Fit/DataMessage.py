#!/usr/bin/env python

#
# copyright Tom Goetz
#

import collections

from DataField import DataField


class DataMessage():

    def __init__(self, definition_message, file, english_units=False):
        self.definition_message = definition_message

        self._fields = {}
        self.file_size = 0
        self._timestamp = None

        fields = {}
        for index in xrange(definition_message.field_count()):
            data_field = DataField(file, definition_message, definition_message.field_definitions[index], english_units)
            self.file_size += data_field.file_size

            # expand subfields?
            field_value = data_field.value()
            subfield_names = field_value.subfield_names()
            if subfield_names:
                for subfield_name in subfield_names:
                    subfield_value = field_value[subfield_name]
                    subfield_formal_name = subfield_value.field.name
                    if subfield_formal_name in fields.keys():
                        fields[subfield_formal_name]._value['value'] += subfield_value._value['value']
                    else:
                        fields[subfield_formal_name] = subfield_value
            else:
                fields[data_field.name()] = data_field.value()

        # expand dependent message fields by message type?
        if self.name() == 'monitoring':
            self.rewrite_monitoring_message(fields)
        else:
            field_names = fields.keys()
            for field_name in field_names:
                self._fields[field_name] = fields[field_name]

    def rewrite_monitoring_message(self, fields):
        field_names = fields.keys()

        if 'activity_type' in field_names:
            activity_type_field = fields['activity_type']
            activity_type_name = activity_type_field.value()
            activity_type_units = activity_type_field.units()
            activity_type_cycles_factor = activity_type_field.field.cycles_factor(activity_type_field['orig'])

        rewritable_field_names = ['cum_active_time', 'active_calories', 'distance', 'duration_min']

        for field_name in field_names:
            field = fields[field_name]
            if field_name == "cycles":
                field.scale_value(activity_type_cycles_factor)
                self._fields[activity_type_name + "_" + activity_type_units] = field
            elif field_name in rewritable_field_names:
                self._fields[activity_type_name + "_" + activity_type_units] = field
            else:
                self._fields[field_name] = field


    def type(self):
        return self.definition_message.message_number()

    def name(self):
        return self.definition_message.name()

    def timestamp(self):
        return self._timestamp

    def __getitem__(self, name):
        if name in self._fields:
            return self._fields[name]
        return None

    def __iter__(self):
        return iter(self._fields)

    def keys(self):
        return self._fields.keys()

    def items(self):
        return self._fields.items()

    def values(self):
        return self._fields.values()

    def __str__(self):
        fields_str = ''
        for field_name in self._fields.keys():
            fields_str += str(self._fields[field_name]) + ","
        return ("%s: %s (%d): %s" % (self.__class__.__name__,  self.name(), self.type(), fields_str))