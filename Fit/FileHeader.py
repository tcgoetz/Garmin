#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from Data import Data

class FileHeader(Data):

    primary_schema = collections.OrderedDict(
        [ ('header_size', ['UINT8', 1, '%d']), ('protocol_version', ['UINT8', 1, '%x']), ('profile_version', ['UINT16', 1, '%d']),
          ('data_size', ['UINT32', 1, '%d']), ('data_type', ['CHAR', 4, '%c']) ]
    )
    optional_schema = collections.OrderedDict(
        [ ('crc', ['UINT16', 1, '%x']) ]
    )
    profile_version_str = { 100: 'activity', 1602 : 'device'}

    min_file_header_size = 12
    opt_file_header_size = 14
    protocol_version = 0x10
    file_data_type = [46, 70, 73, 84]

    def __init__(self, file):
        Data.__init__(self, file, FileHeader.primary_schema, FileHeader.optional_schema)

    def check(self):
        return ((self.decoded_data['header_size'] >= FileHeader.min_file_header_size) and
                (self.decoded_data['protocol_version'] == FileHeader.protocol_version) and
                (self.decoded_data['data_type'] == FileHeader.file_data_type))

    def decode_optional(self):
        return (self.decoded_data['header_size'] >= FileHeader.opt_file_header_size)

    def data_size(self):
        return self.decoded_data['data_size']

    def data_size(self):
        return self.decoded_data['data_size']
