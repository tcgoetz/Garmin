#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from Data import Data
from Field import ( Field, ManufacturerField, ProductField, TimestampField, TimeField, StringField, UnknownField, FileField, VersionField,
                    EventField, EventTypeField, ActivityField, ActivityTypeField, PosField, AltField, LapTriggerField,
                    SportField, SubSportField, SessionTriggerField, GenderField, HeightField, WeightField, PercentField )
from FieldDefinition import FieldDefinition


class DefinitionMessage(Data):

    primary_schema = collections.OrderedDict(
        [ ('reserved', ['UINT8', 1, '%x']), ('architecture', ['UINT8', 1, '%x']) ]
    )
    secondary_schema = collections.OrderedDict(
        [ ('global_message_number', ['UINT16', 1, '%x']), ('fields', ['UINT8', 1, '%x']) ]
    )
    message_number_data = {
        0   : [ 'file_id', { 0: FileField('type'), 1 : ManufacturerField('manufacturer'), 2 : ProductField('product'),
                             3 : Field('serial_number'), 4: TimestampField('time_created'), 5 : Field('number'),
                             7 : StringField('product_name') } ],
        1   : [ 'capabilities', {} ],
        2   : [ 'device_settings', {} ],
        3   : [ 'user_profile', { 1 : GenderField(), 2 : Field('age'), 3 : HeightField(), 4 : WeightField(), 22 : Field('local_id') } ],
        4   : [ 'hrm_profile', {} ],
        5   : [ 'sdm_profile', {} ],
        6   : [ 'bike_profile', {} ],
        7   : [ 'zones_target', {} ],
        8   : [ 'hr_zone', {} ],
        9   : [ 'power_zone', {} ],
        10  : [ 'met_zone', {} ],
        12  : [ 'sport', {} ],
        15  : [ 'goal', {} ],
        18  : [ 'session', { 0 : EventField(), 1 : EventTypeField(), 2: TimestampField('start_time'),
                             3 : PosField('start_position_lat'), 4 : PosField('start_position_long'),
                             5 : SportField(), 6 : SubSportField(),  7 : TimeField('total_elapsed_time'), 8 : TimeField('total_timer_time'),
                             9 : Field('total_distance'),  11 : Field('total_calories'), 13 : Field('total_fat_calories'),
                             14 : Field('avg_speed'), 15 : Field('max_speed'), 22 : Field('total_ascent'), 23 : Field('total_descent'),
                             25 : Field('first_lap_index'), 26 : Field('num_laps'), 28 : SessionTriggerField() } ],
        19  : [ 'lap', { 0 : EventField(), 1 : EventTypeField(), 2: TimestampField('start_time'),
                         3 : PosField('start_position_lat'), 4 : PosField('start_position_long'),
                         5 : PosField('end_position_lat'), 6 : PosField('end_position_long'),
                         7 : TimeField('total_elapsed_time'), 8 : TimeField('total_timer_time'),
                         9 : Field('total_distance'), 11 : Field('total_calories'), 12 : Field('total_fat_calories'),
                         13 : Field('avg_speed'), 14 : Field('max_speed'),
                         21 : Field('total_ascent'), 22 : Field('total_descent'),  24 : LapTriggerField(), 25 : SportField() } ],
        20  : [ 'record', { 0 : PosField('position_lat'), 1 : PosField('position_long'), 2 : AltField('altitude'),
                            3 : Field('heart_rate'), 4 : Field('cadence'), 5 : Field('distance'), 6 : Field('speed'), } ],
        21  : [ 'event', { 0 : EventField(), 1 : EventTypeField(), 2 : Field('data'), 3 : Field('timer_trigger'), 4 : Field('event_group') } ],
        22  : [ 'source', {} ],
        23  : [ 'device_info', { 2 : ManufacturerField('manufacturer'), 3 : Field('serial_number'),
                                 4 : ProductField('garmin_product'), 5 : VersionField('software_version'),
                                 6 : Field('hardware_version'), 7 : Field('cum_operating_time'), 10 : Field('battery_voltage') } ],
        24  : [ 'unknown',  { } ],
        25  : [ 'workout', {} ],
        25  : [ 'workout_step', {} ],
        28  : [ 'schedule', {} ],
        29  : [ 'location', {} ],
        30  : [ 'weight_scale', { 0 : WeightField(), 1 : PercentField('percent_fat'), 12 : Field('user_profile_index') } ],
        31  : [ 'course', {} ],
        32  : [ 'course_point', {} ],
        33  : [ 'totals', {} ],
        34  : [ 'activity', { 0 : TimeField('total_timer_time'), 1 : Field('num_sessions'), 2 : ActivityField(),
                              3 : EventField(), 4 : EventTypeField(), 5 : TimestampField('local_timestamp', False) } ],
        35  : [ 'software', { 3 : VersionField('version') } ],
        37  : [ 'file_capabilities', {} ],
        38  : [ 'mesg_capabilities', {} ],
        39  : [ 'field_capabilities', {} ],
        49  : [ 'file_creator', { 0 : VersionField('software_version')} ],
        51  : [ 'blood_pressure', {} ],
        53  : [ 'speed_zone', {} ],
        55  : [ 'monitoring', { 3 : Field('cycles'), 4 : Field('active_time'), 5 : ActivityTypeField(),
                                19 : Field('active_calories'),
                                31 : Field('ascent'), 32 : Field('descent'),
                                24 : Field('current_activity_type_intensity'), 26 : Field('timestamp_16'), 29 : Field('duration_min'),
                                27 : Field('heart_rate') } ],
        72  : [ 'training_file', {} ],
        78  : [ 'hrv', {} ],
        80  : [ 'ant_rx', {} ],
        81  : [ 'ant_tx', {} ],
        82  : [ 'ant_channel_id', {} ],
        101 : [ 'length', {} ],
        103 : [ 'monitoring_info', { 0 : TimestampField('local_timestamp', False), 1 : ActivityTypeField(),
                                     3 : Field('cycles_to_distance'), 4 : Field('cycles_to_calories'),
                                     5 : Field('resting_metabolic_rate') } ],
        104 : [ 'battery', {} ],
        105 : [ 'pad', {} ],
        106 : [ 'slave_device', {} ],
        127 : [ 'connectivity', {} ],
        128 : [ 'weather_conditions', {} ],
        129 : [ 'weather_alert', {} ],
        131 : [ 'cadence_zone', {} ],
        132 : [ 'hr', {} ],
        142 : [ 'segment_lap', {} ],
        145 : [ 'memo_glob', {} ],
        147 : [ 'sensor', {} ],
        148 : [ 'segment_id', {} ],
        149 : [ 'segment_leaderboard_entry', {} ],
        150 : [ 'segment_point', {} ],
        151 : [ 'segment_file', {} ],
        160 : [ 'gps_metadata', {} ],
        161 : [ 'camera_event', {} ],
        162 : [ 'timestamp_correlation', {} ],
        164 : [ 'gyroscope_data', {} ],
        165 : [ 'accelerometer_data', {} ],
        167 : [ 'three_d_sensor_calibration', {} ],
        169 : [ 'video_frame', {} ],
        174 : [ 'obdii_data', {} ],
        177 : [ 'nmea_sentence', {} ],
        178 : [ 'aviation_attitude', {} ],
        184 : [ 'video', {} ],
        185 : [ 'video_title', {} ],
        186 : [ 'video_description', {} ],
        187 : [ 'video_clip', {} ],
        200 : [ 'exd_screen_configuration', {} ],
        201 : [ 'exd_data_field_configuration', {} ],
        202 : [ 'exd_data_concept_configuration', {} ],
        206 : [ 'field_description', {} ],
        207 : [ 'dev_data_id', {} ],
        208 : [ 'magnetometer_data', {} ],
        211 : ['unknown', { } ],
        0xFF00  : 'mfg_range_min',
        0xFFFE  : 'mfg_range_max',
    }
    reserved_field_indexes = {
        250 : Field('part_index'),
        253 : TimestampField(),
        254 : Field('message_index')
    }
    architecture_table = { 0 : 'Little Endian', 1 : 'Big Endian'}

    def __init__(self, record_header, file):
        Data.__init__(self, file, DefinitionMessage.primary_schema, DefinitionMessage.secondary_schema)
        self.record_header = record_header
        self.field_definitions = []
        for index in xrange(self.field_count()):
            field_definition = FieldDefinition(file)
            self.file_size += field_definition.file_size
            self.field_definitions.append(field_definition)

    def decode_optional(self):
        self.endian = self.architecture()
        return True

    def architecture(self):
        return self.decoded_data['architecture']

    def architecture_str(self):
        return DefinitionMessage.architecture_table[self.architecture()]

    def field_count(self):
        return self.decoded_data['fields']

    def message_number(self):
        gmn = self.decoded_data['global_message_number']
        if (gmn < 0) or (gmn > 0xFFFE):
            raise ValueError('Definition Message message number out of bounds: %d' % gmn)
        return gmn

    def message_data(self):
        try:
            message_data = DefinitionMessage.message_number_data[self.message_number()]
        except:
             raise IndexError("Unknown message number: %d" % self.message_number())
        return message_data

    def name(self):
        return (self.message_data())[0]

    def fields(self):
        return (self.message_data())[1]

    def field(self, index):
        # first check for reserved indexes
        try:
            field = DefinitionMessage.reserved_field_indexes[index]
        except:
            try:
                field = self.fields()[index]
            except:
                field = UnknownField()
        return (field)

    def __str__(self):
        return ("%s: %s (%d) %d %s fields" %
                (self.__class__.__name__, self.name(), self.message_number(), self.field_count(), self.architecture_str()))
