#!/usr/bin/env python

#
# copyright Tom Goetz
#

import collections

from Field import Field
from FieldStats import FieldStats
from DataField import DataField


class DataMessage():

    def __init__(self, definition_message, file, english_units=False):
        self.definition_message = definition_message

        self._fields = {}
        self.file_size = 0
        self._timestamp = None

        field_values = {}
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
                    if subfield_formal_name in field_values.keys():
                        field_values[subfield_formal_name]._value['value'] += subfield_value._value['value']
                    else:
                        field_values[subfield_formal_name] = subfield_value
            else:
                field_values[data_field.name()] = data_field.value()

        # expand dependent message fields by message type?
        if self.name() == 'monitoring':
            self.rewrite_monitoring_message(field_values)
        else:
            field_names = field_values.keys()
            for field_name in field_names:
                self._fields[field_name] = field_values[field_name]

    def rewrite_monitoring_message(self, field_values):
        field_names = field_values.keys()

        if 'activity_type' in field_names:
            activity_type_field_value = field_values['activity_type']
            activity_type_name = activity_type_field_value.value()
            activity_type_units = activity_type_field_value.units()
            activity_based_name = activity_type_name + "_" + activity_type_units
            activity_type_cycles_factor = activity_type_field_value.field.cycles_factor(activity_type_field_value['orig'])
            activity_type_cycles_stats_mode = activity_type_field_value.field.cycles_stats_mode(activity_type_field_value['orig'])

        rewritable_field_names = ['cum_active_time', 'active_calories', 'distance', 'duration_min']

        for field_name in field_names:
            field_value = field_values[field_name]
            if field_name == "cycles":
                field_value.scale_value(activity_type_cycles_factor)
                field_value.field = Field(activity_based_name, stats_mode=activity_type_cycles_stats_mode)
                self._fields[activity_based_name] = field_value
            elif field_name in rewritable_field_names:
                field_value.field = Field(activity_based_name, stats_mode=activity_type_cycles_stats_mode)
                self._fields[field_name + "_" + activity_type_name] = field_value
            else:
                self._fields[field_name] = field_value


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