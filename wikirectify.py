#!/usr/bin/env python3

import argparse
import pymysql
import requests
import logging
from urllib.parse import urlunparse
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

    min_lang_default = 4
    parser.add_argument(
            '-n',
            '--number',
            help='minimum number of language links required to keep entry.'\
            'Default to {}.'.format(min_lang_default),
            default=min_lang_default
            )

    args = parser.parse_args()
    wikirectify(
            args.host,
            args.username,
            args.password,
            args.database,
            args.number)

    return

def wikirectify(host,user,passwd,db,number):
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
    table_list_query = "select TABLE_NAME from information_schema.tables"\
            " where TABLE_SCHEMA=%s"

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
            lang_links = lang_links(remote_id,remote_wiki_host)
            if len(lang_links) < number:
                remove_poi(connection, remote_id)
            else:
                coordinates = [geocoord(wiki) for wiki in lang_links]
                # compute the average

        cursor.close()

    connection.close()

            # get all the language link for that entry.
            # if the number of language links is less then 4, remove that entry
            # and continue.
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
    pageid. Language links will include the page beeing queried.
    """

    # language link request.
    params = {
            "action":"query",
            "pageids":pageid,
            "prop":"langlinks",
            "llprop":"url",
            "lllimit":500,
            "format":"json",
            }

    r = requests.get(endpoint, params=params)

    raw_result = None
    try:
        raw_result = r.json()
    except Exception as e:
        logging.error('json response parsing failed for {} using.'\
                '{}. Language list returned will be empty'.format(pageid,
                    endpoint))
        return []

    page = None
    try:
        page = raw_result['query']['pages'][str(pageid)]
    except Exception as e:
        logging.error('the endpoint {} did not return pageid {}'\
                ' Language list returned will be empty'.format(endpoint,
                    page_id))
        return []

    lang_links = None
    try:
        lang_links = page['langlinks']
    except Exception as e:
        logging.error('there was not language links for {} using {}'\
                ' Language list returned is empty.'.format(pageid,endpoint))
        return []

    result = []
    for link in lang_links:
        try:
            url = link['url']
            result.append(url)
        except Exception as e:
            logging.error('no url for {}'.format(link))

    # append the url of the current page too.
    self_url = full_url(endpoint,pageid)

    if self_url:
        result.append(self_url)

    return result

def full_url(endpoint, pageid):
    """
    returns the full url of a page given it's id on endpoint.
    """

    params = {
            "action":"query",
            "format":"json",
            "prop":"info",
            "inprop":"url",
            "pageids":pageid
            }

    r = requests.get(endpoint, params=params)

    raw_result = None
    try:
        raw_result = r.json()
    except Exception as e:
        logging.error('could not query {} on {}. Full url will not be added'\
                ' to the list.'.format(pageid,endpoint))
        return None

    url = None
    try:
        url = raw_result['query']['pages'][str(pageid)]['fullurl']
    except Exception as e:
        logging.error('api response for {} on {} did not contain a full url.'\
                ' Will not be added to the list.'.format(pageid, endpoint))
        return None

    return url

def wiki_api_host(table_name):
    """
    Returns the hostname of the wiki api endpoint corresponding to the given
    table_name.
    """

    lang = lang_code(table_name)
    parts = ('http', '{}.wikipedia.org'.format(lang), '/w/api.php', '', '', '')

    result = urlunparse(parts)
    return result


def lang_code(table_name):
    """
    Returns the language code contained in the table_name.
    """

    prefix = 'coord_'
    suffix = 'wiki'

    result = table_name

    valid = table_name.startswith(prefix) and table_name.endswith(suffix)
    if not valid:
        raise Exception('{} is not a valid table_name'.format(table_name))

    result = table_name[len(prefix):-len(suffix)]
    return result

if __name__ == '__main__':
    main()

