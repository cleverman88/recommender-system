# !/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
#
# (c) Copyright University of Southampton, 2021
#
# Copyright in this software belongs to University of Southampton,
# Highfield, University Road, Southampton SO17 1BJ
#
# Created By : Stuart E. Middleton
# Created Date : 2021/02/11
# Project : Teaching
#
######################################################################

from __future__ import absolute_import, division, print_function, unicode_literals

import codecs, logging, sqlite3

"""
    Class to handle the database functions, designed for test guesses and real guesses
"""


class DBHandler:
    """
        Creates the logger and sets up the tables
    """

    def __init__(self):
        LOG_FORMAT = ('%(levelname) -s %(asctime)s %(message)s')
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        self.logger.info('logging started')
        self.test_conn = sqlite3.connect('dbs/test_table.db')
        self.real_conn = sqlite3.connect('dbs/real_table.db')
        self.test_c = self.test_conn.cursor()
        self.real_c = self.real_conn.cursor()

    """
        Reads a database given the name
    """

    def read_data(self, name):
        self.logger.info("Reading data from database: " + name)
        read_handle = codecs.open('csv/' + name + '', 'r', 'utf-8', errors='replace')
        list_lines = read_handle.readlines()
        read_handle.close()
        return list_lines

    """
        Creates and sets up the test table 
    """

    def setup_test_table(self):
        self.logger.info("Setting up test table")
        self.test_c.execute(
            'CREATE TABLE IF NOT EXISTS test_table (UserID INT, ItemID INT, Rating INT, PredRating FLOAT)')
        self.test_conn.commit()
        self.test_c.execute('DELETE FROM test_table')
        self.test_conn.commit()

    """
        Creates and sets up the real table 
    """

    def setup_real_table(self):
        self.logger.info("Setting up real table")
        self.real_c.execute(
            'CREATE TABLE IF NOT EXISTS real_table (UserID INT, ItemID INT, Rating INT)')
        self.real_conn.commit()
        self.real_c.execute('DELETE FROM real_table')
        self.real_conn.commit()

    """
        Function for inserting into the real table
    """

    def insert_into_real_table(self, userid, itemid, predict):
        self.test_c.execute('INSERT INTO test_table VALUES (?,?,?)',
                            (userid, itemid, predict))

    """
        Function for inserting into the test table
    """

    def insert_into_test_table(self, userid, itemid, rating, predict):
        self.test_c.execute('INSERT INTO test_table VALUES (?,?,?,?)',
                            (userid, itemid, rating, predict))

    """
        Calculates the MSE for the test table
    """

    def calculate_test_mse(self):
        # Creating an index first
        self.test_conn.commit()
        self.test_c.execute('CREATE INDEX IF NOT EXISTS test_table_index on test_table (UserID, ItemID)')
        self.test_conn.commit()
        # Calculating MSE
        self.test_c.execute('SELECT AVG(ABS(Rating-PredRating)) FROM test_table WHERE PredRating IS NOT NULL')
        row = self.test_c.fetchone()
        nMSE = float(row[0])
        self.logger.info('MSE for prediction = ' + str(nMSE))

    """
        Closes all the connections
    """
    def end(self):
        self.test_c.close()
        self.test_conn.close()
        self.real_c.close()
        self.real_conn.close()
