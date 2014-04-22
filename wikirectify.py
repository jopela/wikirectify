#!/usr/bin/env python3

import argparse
import pymysql

def main():
    """
    Rectify the coordinates of some POI in the mtrip database
    """

    parser = argparse.ArgumentParser()

    host_default = 'mtrip-linker'
    parser.add_argument(
            '-H',
            '--host',
            help='hostname of the database. Default to {}'.format(host_default),
            default = host_default
            )

    parser.add_argument(
            '-u',
            '--username',
            help='username of the account used to connect to the DB.',
            required = True
            )

    parser.add_argument(
            '-p',
            '--password',
            help='password of the account used to connect tot he DB',
            required = True
            )

    print_default = False
    parser.add_argument(
            '-P',
            '--print',
            help='print the SQL statement generated but do not run them against the database.',
            default=print_default
            )

    database_default = 'Linker'
    parser.add_argument(
            '-d',
            '--database',
            help='Database in which the wiki tables will be located. Default to {}'.format(database_default),
            default=database_default
            )

    args = parser.parse_args()
    print(args)

    return

def wikirectify(host,user,passwd,db):
    """
    Modify the coordinates of the POI for the wiki database.
    """

    # connect to the database.
    connection = pymysql.connect(host=host,
    # get the list of tables that are wikitables.
    # for all tables,
        # for all entry in the table
            # get the id and the coordinates of the entry.
            # get all the language link for that entry.
            # if the number of language links is less then 4, remove that entry and continue.
            # for all language links
                # get the coordinate for that entry

            # compute the variance fo the coordinates
            # reject the coordinates that are not within [avg-sigma, avg+sigma]
            # if no coordinates left, remove the entry and continue.
            # compute the average.
            # update the coordinate with the computed average


    return

if __name__ == '__main__':
    main()

