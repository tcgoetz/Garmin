#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from Data import Data

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