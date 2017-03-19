#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, collections

from FileHeader import FileHeader
from RecordHeader import RecordHeader
from DefinitionMessage import DefinitionMessage
from DataMessage import DataMessage


class FitParseError(Exception):
    pass


class File():

    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.parse()

    def parse(self):
        self.file_header = FileHeader(self.file)
        if not self.file_header.check():
            logging.error("Bad header: " + str(self.file_header))
            return False

        self.data_size = self.file_header.get_data_size()

        self.definition_messages = {}
        self.data_messages = {}
        data_consumed = 0
        self.record_count = 0

        while self.data_size > data_consumed:
            record_header = RecordHeader(self.file)
            local_message_num = record_header.local_message()
            data_consumed += record_header.file_size
            self.record_count += 1

            if record_header.definition_message():
                definition_message = DefinitionMessage(record_header, self.file)
                data_consumed += definition_message.file_size
                self.definition_messages[local_message_num] = definition_message

            elif record_header.data_message():
                data_message = DataMessage(self.definition_messages[local_message_num], self.file)
                data_consumed += data_message.file_size

                try:
                    self.data_messages[data_message.name()].append(data_message)
                except:
                    self.data_messages[data_message.name()] = [ data_message ]

            #logging.debug("Record %d: consumed %d of %s" % (self.record_count, data_consumed, self.data_size))

    def type(self):
        return self['file_id'][0]['type']

    def time_created(self):
        return self['file_id'][0]['time_created']

    def __getitem__(self, name):
        return self.data_messages[name]


