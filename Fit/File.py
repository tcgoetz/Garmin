#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, struct, collections

from datetime import tzinfo, timedelta, datetime
from time import time, gmtime, localtime


class FitParseError(Exception):
    pass


class Data():

    def __init__(self, file, schema):
        self.file = file
        self.schema = schema
        self.decode()
        logging.debug(str(self))

    def type_to_size(self, type):
        type_size = { 'CHAR' : 1, 'INT8' : 1, 'UINT8' : 1, 'INT16' : 2, 'UINT16' : 2, 'INT32' : 4, 'UINT32' : 4,
                      'INT64' : 8, 'UINT64' : 8, 'FLOAT32' : 4, 'FLOAT64' : 4}
        return type_size[type]

    def type_to_unpack_format(self, type):
        type_size = { 'CHAR' : 'B', 'INT8' : 'b', 'UINT8' : 'B', 'INT16' : 'h', 'UINT16' : 'H', 'INT32' : 'i',
                      'UINT32' : 'I', 'INT64' : 'q', 'UINT64' : 'Q', 'FLOAT32' : 'f', 'FLOAT64' : 'd'}
        return type_size[type]

    def read(self):
        unpack_format = ''
        self.file_size = 0
        for key in self.schema:
            (type, count, format) = self.schema[key]
            # logging.debug("Key %s type %s Count %d" % (key, type, count))
            for index in xrange(count):
                unpack_format += self.type_to_unpack_format(type)
            self.file_size += (count * self.type_to_size(type))
        # logging.debug("Reading (%d : %s) from %s" % (size, unpack_format, self.file))
        return struct.unpack(unpack_format, self.file.read(self.file_size))

    def decode(self):
        data = self.read()
        decoded_data = {}
        index = 0
        for key in self.schema:
            (type, count, format) = self.schema[key]
            if count > 1:
                decoded_data[key] = []
                for repeat in xrange(count):
                    # logging.debug("Index %d data %x" % (index, data[index]))
                    decoded_data[key].append(data[index])
                    index += 1
            else:
                    # logging.debug("Index %d data %x" % (index, data[index]))
                    decoded_data[key] = data[index]
                    index += 1
        self.decoded_data = decoded_data

    def __str__(self):
        printable_data = {}
        for key in self.schema:
            (type, count, format) = self.schema[key]
            if count > 1:
                printable_data[key] = []
                for index in xrange(count):
                    values = self.decoded_data[key]
                    # logging.debug("Key %s data %x" % (key, values[index]))
                    printable_data[key].append(format % values[index])
            else:
                    # logging.debug("Key %s data %x" % (key, self.decoded_data[key]))
                    printable_data[key] = (format % self.decoded_data[key])
        return (self.__class__.__name__ + " : " + str(printable_data))


class FileHeader(Data):

    schema = collections.OrderedDict(
        [ ('header_size', ['UINT8', 1, '%d']), ('protocol_version', ['UINT8', 1, '%x']), ('profile_version', ['UINT16', 1, '%d']),
          ('data_size', ['UINT32', 1, '%d']), ('data_type', ['CHAR', 4, '%c']), ('crc', ['UINT16', 1, '%x'])]
    )

    file_header_size = 14
    protocol_version = 0x10
    file_data_type = [46, 70, 73, 84]
    profile_version = 1602

    def __init__(self, file):
        Data.__init__(self, file, FileHeader.schema)

    def check(self):
        return ((self.decoded_data['header_size'] == FileHeader.file_header_size) and
                (self.decoded_data['protocol_version'] == FileHeader.protocol_version) and
                (self.decoded_data['data_type'] == FileHeader.file_data_type) and
                (self.decoded_data['profile_version'] == FileHeader.profile_version))

    def data_size(self):
        return self.decoded_data['data_size']


class RecordHeader(Data):

    schema = collections.OrderedDict( [ ('record_header', ['UINT8', 1, '%x']) ] )
    message_type_string = [ 'data', 'definition' ]

    def __init__(self, file):
        Data.__init__(self, file, RecordHeader.schema)

    def record_header(self):
        return self.decoded_data['record_header']

    def compressed_timestamp(self):
        return (self.record_header() & 0x80) >> 7

    def message_type(self):
        return (self.record_header() & 0x40) >> 6

    def message_type_str(self):
        return RecordHeader.message_type_string[self.message_type()]

    def definition_message(self):
        return self.message_type()

    def data_message(self):
        return not self.message_type()

    def local_message(self):
        return (self.record_header() & 0x0f)

    def __str__(self):
        return ("%s: Local %s message %d (Compressed %d)" %
                (self.__class__.__name__, self.message_type_str(), self.local_message(), self.compressed_timestamp()))


class Field():

    def __init__(self, name, type='number'):
        self.name = name
        self.type = type

    def convert(self, value):
        return value

    def display(self, value):
        return (self.name + " : " + self.type + " : " + str(self.convert(value)))

    def __str__(self):
        return (self.__class__.__name__ + " : " + self.name)


class ManufacturerField(Field):

    manufacturer = { 1 : 'Garmin' }

    def __init__(self, name):
        Field.__init__(self, name, 'manufacturer')

    def convert(self, value):
        return ManufacturerField.manufacturer[value];


class ProductField(Field):

    product = { 2337 : 'VivoActive HR' }

    def __init__(self, name):
        Field.__init__(self, name, 'product')

    def convert(self, value):
        return ProductField.product[value];


class TimestampField(Field):

    def __init__(self, name, utc=True):
        self.utc = utc
        Field.__init__(self, name, 'date_time')

    def convert(self, value):
        if self.utc:
            timestamp = time()
            time_now = datetime.fromtimestamp(timestamp)
            time_utc = datetime.utcfromtimestamp(timestamp)
            utc_offset_secs = (time_now - time_utc).total_seconds()
            value += utc_offset_secs
        timestamp = datetime(1989, 12, 31, 0, 0, 0) +  timedelta(0, value)
        return timestamp.isoformat();


class StringField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'string')

    def convert(self, value):
        return value


class UnknownField(Field):

    def __init__(self):
        Field.__init__(self, 'unknown')


class FileField(Field):

    file_types = { 1 : 'device', 2 : 'settings', 3 : 'sport', 4 : 'activity', 5 : 'workout', 6 : 'course', 7 : 'schedules',
                    9 : 'weight', 10 : 'totals', 11 : 'goals', 14 : 'blood_pressure', 15 : 'monitoring_a', 20 : 'activity_summary',
                    28 : 'monitoring_daily', 32 : 'monitoring_b', 34 : 'segment', 35 : 'segment_list', 40 : 'exd_configuration' }

    def __init__(self, name):
        Field.__init__(self, name, 'file')

    def convert(self, value):
        return FileField.file_types[value]


class VersionField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'version')

    def convert(self, value):
        return (value)


class EventField(Field):

    event = { 0 : 'timer', 3 : 'workout', 4 : 'workout_step', 5 : 'power_down', 6 : 'power_up', 7 : 'off_course', 8 : 'session',
              9 : 'lap', 10 : 'course_point', 11 : 'battery', 12 : 'virtual_partner_pace', 13 : 'hr_high_alert', 14 : 'hr_low_alert',
              15 : 'speed_high_alert', 16 : 'speed_low_alert', 17 : 'cad_high_alert', 18 : 'cad_low_alert', 19 : 'power_high_alert',
              20 : 'power_low_alert', 21 : 'recovery_hr', 22 : 'battery_low', 23 : 'time_duration_alert', 24 : 'distance_duration_alert',
              25 : 'calorie_duration_alert', 26 : 'activity', 27 : 'fitness_equipment', 28 : 'length', 32 : 'user_marker',
              33 : 'sport_point', 36 : 'calibration', 42 : 'front_gear_change', 43 : 'rear_gear_change', 44 : 'rider_position_change',
              45 : 'elev_high_alert', 46 : 'elev_low_alert', 47 : 'comm_timeout', 54 : 'unknown' }

    def __init__(self):
        Field.__init__(self, 'event', 'event')

    def convert(self, value):
        return EventField.event[value]


class EventTypeField(Field):

    type = { 0 : 'start', 1 : 'stop', 2 : 'consecutive_depreciated', 3 : 'marker', 4 : 'stop_all', 5 : 'begin_depreciated',
                   6 : 'end_depreciated', 7 : 'end_all_depreciated', 8 : 'stop_disable', 9 : 'stop_disable_all'}

    def __init__(self):
        Field.__init__(self, 'event_type', 'event_type')

    def convert(self, value):
        return EventTypeField.type[value]


class ActivityTypeField(Field):

    type = { 0 : 'generic', 1 : 'running', 2 : 'cycling', 3 : 'transition', 4 : 'fitness_equipment', 5 : 'swimming',
                   6 : 'walking', 8 : 'sedentary', 8 : 'stop_disable', 245 : 'all'}

    def __init__(self):
        Field.__init__(self, 'activity_type', 'activity_type')

    def convert(self, value):
        return ActivityTypeField.type[value]


class FieldDefinition(Data):

    schema = collections.OrderedDict(
        [ ('field_definition_number', ['UINT8', 1, '%x']), ('size', ['UINT8', 1, '%x']), ('base_type', ['UINT8', 1, '%x']) ]
    )
    base_type_data = {
        0x00 : [ False, 'enum',     0xFF,               'UINT8'],
        0x01 : [ False, 'sint8',    0x7F,               'INT8'],
        0x02 : [ False, 'uint8',    0xFF,               'UINT8'],
        0x07 : [ False, 'string',   0x00,               'CHAR'],
        0x83 : [ True,  'sint16',   0x7FFF,             'INT16'],
        0x84 : [ True,  'uint16',   0xFFFF,             'UINT16'],
        0x85 : [ True,  'sint32',   0x7FFFFFFF,         'INT32'],
        0x86 : [ True,  'uint32',   0xFFFFFFFF,         'UINT32'],
        0x88 : [ True,  'float32',  0xFFFFFFFF,         'FLOAT32'],
        0x89 : [ True,  'float64',  0xFFFFFFFFFFFFFFFF, 'FLOAT64'],
        0x0a : [ False, 'uint8z',   0x00,               'UINT8'],
        0x8b : [ True,  'uint16z',  0x00000000,         'UINT16'],
        0x8c : [ True,  'uint32z',  0x00000000,         'UINT32'],
        0x0d : [ False, 'byte',     0xFF,               'UINT8'],
        0x8e : [ True,  'sint64',   0x7FFFFFFFFFFFFFFF, 'INT64'],
        0x8f : [ True,  'uint64',   0xFFFFFFFFFFFFFFFF, 'UINT64'],
        0x90 : [ True,  'uint64z',  0x0000000000000000, 'UINT64'],
    }

    def __init__(self, file):
        Data.__init__(self, file, FieldDefinition.schema)

    def fdn_value(self):
        return self.decoded_data['field_definition_number']

    def size_value(self):
        return self.decoded_data['size']

    def base_type_value(self):
        return self.decoded_data['base_type']

    def base_type(self):
        try:
            base_type = FieldDefinition.base_type_data[self.base_type_value()]
        except:
            raise IndexError("Unknown base type index %d" % self.base_type_value())
        return base_type

    def endian(self):
        return (self.base_type())[0]

    def type_name(self):
        return (self.base_type())[1]

    def invalid(self):
        return (self.base_type())[2]

    def type_string(self):
        return (self.base_type())[3]

    def type_count(self):
        type_size = self.type_to_size(self.type_string())
        return (self.size_value() / type_size)

    def __str__(self):
        return ("%s: type %d: %d of [endian %d name %s invalid %x type_name %s]" %
                (self.__class__.__name__, self.fdn_value(), self.size_value(), self.endian(), self.type_name(),
                 self.invalid(), self.type_string()));

class DefinitionMessage(Data):

    schema = collections.OrderedDict(
        [ ('reserved', ['UINT8', 1, '%x']), ('architecture', ['UINT8', 1, '%x']), ('global_message_number', ['UINT16', 1, '%x']),
          ('fields', ['UINT8', 1, '%x']) ]
    )
    message_number_data = {
        0   : [ 'file_id', { 0: Field('type'), 1 : ManufacturerField('manufacturer'), 2 : ProductField('product'),
                             3 : Field('serial_number'), 4: TimestampField('time_created'), 5 : Field('number'),
                             6 :  UnknownField(), 7 : StringField('product_name') } ],
        1   : 'capabilities',
        2   : 'device_settings',
        3   : 'user_profile',
        4   : 'hrm_profile',
        5   : 'sdm_profile',
        6   : 'bike_profile',
        7   : 'zones_target',
        8   : 'hr_zone',
        9   : 'power_zone',
        10  : 'met_zone',
        12  : 'sport',
        15  : 'goal',
        18  : 'session',
        19  : 'lap',
        20  : 'record',
        21  : [ 'event', { 0 : EventField(), 1 : EventTypeField(), 2 : Field('data'),
                           14 : UnknownField(), 15 :UnknownField(), 16 : UnknownField(),
                           253 : TimestampField('timestamp') } ],
        22  : 'source',
        23  : [ 'device_info', { 2 : ManufacturerField('manufacturer'), 3 : Field('serial_number'),
                                 4 : ProductField('garmin_product'), 5 : VersionField('software_version'),
                                 253 : TimestampField('timestamp') } ],
        24  : [ 'workout',  { 2 : UnknownField() } ],
        25  : 'workout_step',
        28  : 'schedule',
        29  : 'location',
        30  : 'weight_scale',
        31  : 'course',
        32  : 'course_point',
        33  : 'totals',
        34  : 'activity',
        35  : [ 'software', { 3 : VersionField('version') } ],
        37  : 'file_capabilities',
        38  : 'mesg_capabilities',
        39  : 'field_capabilities',
        49  : 'file_creator',
        51  : 'blood_pressure',
        53  : 'speed_zone',
        55  : [ 'monitoring', { 2 : UnknownField(), 3 : Field('cycles'), 4 : Field('active_time'), 5 : ActivityTypeField(),
                                19 : Field('active_calories'),
                                31 : Field('ascent'), 32 : Field('descent'),
                                24 : Field('current_activity_type_intensity'), 26 : Field('timestamp_16'), 29 : Field('duration_min'),
                                27 : Field('heart_rate'),
                                35 : UnknownField(), 36 : UnknownField(), 37 : UnknownField(), 38 : UnknownField(),
                                253 : TimestampField('timestamp') } ],
        72  : 'training_file',
        78  : 'hrv',
        80  : 'ant_rx',
        81  : 'ant_tx',
        82  : 'ant_channel_id',
        101 : 'length',
        103 : [ 'monitoring_info', { 0 : TimestampField('local_timestamp', False), 1 : Field('activity_type'),
                                     3 : Field('cycles_to_distance'), 4 : Field('cycles_to_calories'),
                                     5 : Field('resting_metabolic_rate'), 7 : UnknownField(),
                                     8 : UnknownField(), 253 : TimestampField('timestamp') } ],
        104 : 'battery',
        105 : 'pad',
        106 : 'slave_device',
        127 : 'connectivity',
        128 : 'weather_conditions',
        129 : 'weather_alert',
        131 : 'cadence_zone',
        132 : 'hr',
        142 : 'segment_lap',
        145 : 'memo_glob',
        147 : 'sensor',
        148 : 'segment_id',
        149 : 'segment_leaderboard_entry',
        150 : 'segment_point',
        151 : 'segment_file',
        160 : 'gps_metadata',
        161 : 'camera_event',
        162 : 'timestamp_correlation',
        164 : 'gyroscope_data',
        165 : 'accelerometer_data',
        167 : 'three_d_sensor_calibration',
        169 : 'video_frame',
        174 : 'obdii_data',
        177 : 'nmea_sentence',
        178 : 'aviation_attitude',
        184 : 'video',
        185 : 'video_title',
        186 : 'video_description',
        187 : 'video_clip',
        200 : 'exd_screen_configuration',
        201 : 'exd_data_field_configuration',
        202 : 'exd_data_concept_configuration',
        206 : 'field_description',
        207 : 'developer_data_id',
        208 : 'magnetometer_data',
        211 : ['unknown', { 0 : UnknownField(), 1 : UnknownField(), 253 : UnknownField() } ],
        0xFF00  : 'mfg_range_min',
        0xFFFE  : 'mfg_range_max',
    }

    def __init__(self, record_header, file):
        Data.__init__(self, file, DefinitionMessage.schema)
        self.record_header = record_header
        self.field_definitions = []
        for index in xrange(self.field_count()):
            field_definition = FieldDefinition(file)
            self.file_size += field_definition.file_size
            self.field_definitions.append(field_definition)
 
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
        try:
            field = self.fields()[index]
        except:
            raise IndexError("Unknown field index: %d for message (%d) %s" % (index, self.message_number(), self.name()))
        return (field)

    def __str__(self):
        return ("%s: %s (%d) fields (%d) %s" %
                (self.__class__.__name__, self.name(), self.message_number(), self.field_count(), str(self.fields())))


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


class DataMessage():

    def __init__(self, definition_message, file):
        self.definition_message = definition_message

        self.data_fields = []
        self.file_size = 0
        for index in xrange(definition_message.field_count()):
            data_field = DataField(file, definition_message, definition_message.field_definitions[index])
            self.file_size += data_field.file_size
            self.data_fields.append(data_field)


class File():

    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.parse()

    def dump(self, count):
        unpack_format = ''
        print_format_hex = ''
        print_format_char = ''
        for index in xrange(count):
            unpack_format += 'B'
            print_format_hex += '%x ';
            print_format_char += '%c ';
        logging.debug("Dumping (%d : %s) from %s" % (count, unpack_format, self.file))
        bytes = struct.unpack(unpack_format, self.file.read(count))
        print(print_format_hex % bytes)
        print(print_format_char % bytes)

    def parse(self):
        self.file_header = FileHeader(self.file)
        if not self.file_header.check():
            logging.error("Bad header: " + str(self.file_header.printable()))
            return False

        self.data_size = self.file_header.data_size()

        self.definition_messages = {}
        self.data_messages = []
        data_consumed = 0
        self.record_count = 0

        while self.data_size >= data_consumed:
            record_header = RecordHeader(self.file)
            local_message_num = record_header.local_message()
            self.file_size = record_header.file_size
            self.record_count += 1

            if record_header.definition_message():
                definition_message = DefinitionMessage(record_header, self.file)
                data_consumed += definition_message.file_size
                self.definition_messages[local_message_num] = definition_message
            elif record_header.data_message():
                data_message = DataMessage(self.definition_messages[local_message_num], self.file)
                data_consumed += data_message.file_size
                self.data_messages.append(definition_message)

            logging.debug("Record %d: consumed %d of %s" % (self.record_count, data_consumed, self.data_size))

        # self.dump(64)
        
