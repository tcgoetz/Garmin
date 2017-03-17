#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging, struct


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
