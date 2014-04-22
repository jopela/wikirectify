#!/usr/bin/env python3

import argparse
import pymysql
import requests
import logging
from progress.bar import Bar

def main():
    """
    Rectify the coordinates of some POI in the mtrip database
    """

    parser = argparse.ArgumentParser()

    host_default = 'mtrip-linker'
    parser.add_argument(
            '-H',
            '--host',
            help='Database hostname. Default to {}'.format(host_default),
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
            help='password of the account used to connect tot he DB.',
            required = True
            )

    print_default = False
    parser.add_argument(
            '-P',
            '--print',
            help='print the SQL statement generated but do not run them'\
                    'against the database.',
            default=print_default
            )

    database_default = 'Linker'
    parser.add_argument(
            '-d',
            '--database',
            help='Database in which the wiki tables will be located.'\
            'Default to {}.'.format(database_default),
            default=database_default
            )

    args = parser.parse_args()
    wikirectify(args.host, args.username, args.password, args.database)

    return

def wikirectify(host,user,passwd,db):
    """
    Modify the coordinates of the POI for the wiki database.
    """

    # Connect to the database.
    connection = pymysql.connect(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            charset='utf8')
    cursor = connection.cursor()
    table_list_query = "select TABLE_NAME from information_schema.tables'\
            ' where TABLE_SCHEMA=%s"

    cursor.execute(table_list_query, (db,))

    wiki_table_prefix = 'coord_'
    table_names = [row[0] for row in cursor if wiki_table_prefix in row[0]]

    cursor.close()

    for name in table_names:
        cursor = connection.cursor()
        entry_query = "select gc_from, gc_lat, gc_lon from {}".format(name)
        remote_wiki_host = wiki_api_host(name)
        cursor.execute(entry_query)
        for coord in cursor:
            remote_id, lat, lon = coord
            lang_links = wiki_lang_links(remote_id,remote_wiki_host)
            print(remote_id, lat, lon)

        cursor.close()

    connection.close()

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


def lang_links(endpoint,pageid):
    """
    Returns all the language links (full url) of the page having the given
    pageid.
    """

    # See http://en.wikipedia.org/w/api.php for more info on the MediaWiki api.
    params = {
            "action":"query",
            "pageids":pageid,
            "prop":"langlinks",
            "llprop":"url",
            "lllimit":500
            }

    r = requests.get(endpoint, params=params)
    raw_result = None
    try:
        raw_result = r.json()
    except Exception as e:
        logging.error('json response parsing failed for {} using.'\
                ' Language list returned will be empty'.format())
        return []

    result = []

    return result

def wiki_api_host(name):
    """
    Returns the hostname of the wiki api endpoint corresponding to the given table name.

    EXAMPLE
    =======

    >>> wiki_api_host('coord_enwiki')
    'http://en.wikipedia.org/w/api.php'

    >>> wiki_api_host('coord_frwiki')
    'http://fr.wikipedia.org/w/api.php'
    """

    return 'http://mtrip.com'

if __name__ == '__main__':
    main()

