#!/usr/bin/env python3

import argparse
import pymysql
import requests
import logging
import statistics
from urllib.parse import urlunparse
from urllib.parse import urlparse
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
            '--printout',
            help='print the (update/delete) SQL statement generated but do'\
                    'not run them against the database. Select statements'\
                    ' are always executed.',
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

    min_lang_default = 2
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
            args.number,
            args.printout)

    return

def wikirectify(host,user,passwd,db,number,printout):
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
        pbar = Bar('Rectifying coordinates for'\
                ' table {}'.format(name),max=cursor.rowcount())

        for coord in cursor:
            remote_id, lat, lon = coord
            lang_links = lang_links(remote_id,remote_wiki_host)
            if len(lang_links) < number:
                remove_poi(connection, name, remote_id, printout)
            else:
                coords = [
                    geocoords(wiki) for wiki in lang_links if geocoords(wiki)
                    ]

                # we assume that 'good' coordinates are normally distributed.
                # we therefore reject all the coordinates that are 'improbable'
                # and recompute the average. Improbable is

                lats,lons = zip(*coords)
                sigma_lats = statistics.stdev(lats)
                sigma_lons = statistics.stdev(lons)

                mean_lats = statistics.mean(lats)
                mean_lons = statistics.mean(lons)

                probable_coords = [
                        c for c in coords if is_probable( c, mean_lats,
                            mean_lons,
                            sigma_lats,
                            sigma_lons)]

                if len(probable_coords) > 0:
                    lats,lon = zip(*probable_coords)
                    new_lats = statistics.mean(lats)
                    new_lon = statistics.mean(lons)
                    update_poi(connection,
                            name,
                            remoe_id,
                            new_lat,
                            new_lon,
                            printout)
                else:
                # If no coordinates make it pass the filtering, we cannot
                # trust that point and we remove it from the DB.
                    remove_poi(connection, name, remote_id, printout)


            pbar.next()

        cursor.close()
        pbar.finish()

    connection.close()
    return

def update_poi(connection,table_name,gc_from,new_lat,new_lon,printout):
    """
    update the gc_from poi with the new_lat and new_lon.
    """

    update_cursor = connection.cursor()
    query = "update {} set gc_lat=%s, gc_lon=%s where"\
            " gc_from=%s".format(table_name)

    if printout:
        logging.warning("printing in lieu of updating:{}".format(query))
    else:
        update_cursor.execute(query, (new_lat, new_lon, gc_from))

    update_cursor.close()
    return


def is_probable(point,mean_lats,mean_lons,sigma_lats,sigma_lons):
    """
    Returns true if the given points lat and lon both lie within
    2 standard deviation of the means for each coordinates.
    """

    lat,lon = point

    min_lat = mean_lats - (2*sigma_lats)
    max_lat = mean_lats + (2*sigma_lats)

    min_lon = mean_lons - (2*sigma_lons)
    max_lon = mean_lons + (2*sigma_lons)

    return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)


def remove_poi(connection, table_name, gc_from, printout=False):
    """
    Remove the poi from the database.
    """

    del_cursor = connection.cursor()
    query = 'delete from {} where gc_from=%s'.format(table_name)

    if printout:
        logging.warning(query)
    else:
        del_cursor.execute(query,(gc_from,))

    del_cursor.close()
    return

def wiki_title(wiki):
    """
    Returns the 'title' of a given wikilink. Title is the last part of the
    path.
    """

    path = urlparse(wiki).path
    last = path.split('/')[-1]
    return last

def geocoords(wiki):
    """
    Returns a tuple of the form (lat,lon) where lat is the WGS84 latitude of
    the subject of the wikipedia article and lon is the WGS84 longitude of the
    subject of the wikipedia article. If the article has no coordinates, will
    return None.
    """

    endpoint = wiki_api_host_url(wiki)
    page_title = wiki_title(wiki)

    params = {
            "action":"query",
            "format":"json",
            "prop":"coordinates",
            "coprimary":"primary",
            "titles":page_title
            }

    r = requests.get(endpoint, params=params)
    raw_result = None
    try:
        raw_result = r.json()
    except Exception as e:
        logging.error('query for {} did not return a valid'\
                ' json response.'.format(wiki))
        return None

    coordinates = None
    try:
        pages = raw_result['query']['pages']
        pageid = list(pages.keys())[0]
        coords = pages[pageid]['coordinates'][0]
        coordinates = coords['lat'],coords['lon']
    except Exception as e:
        logging.error('{} does not have any associated'\
                ' coordinates.'.format(wiki))
        return None

    return coordinates

def wiki_api_host_url(wiki):
    """
    returns the api endpoint of the wiki instance where we can find the wiki
    article.
    """

    parts = urlparse(wiki)

    new_parts = (parts[0],parts[1],'/w/api.php','','','')
    result = urlunparse(new_parts)

    return result

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

