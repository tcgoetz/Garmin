#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging


class OutputData():

    def __init__(self, file):
        self.file = file
        self.entries = []

        self.parse()

    def parse(self):
        self.parse_info()
        self.parse_messages()

    def fields(self):
        return self.entries

    def __getitem__(self, index):
        return self.entries[index]
