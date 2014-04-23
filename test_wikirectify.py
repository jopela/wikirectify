import wikirectify

def test_lang_links():
    """
    Must return a list of the language links from a live wikipedia instance.
    """
    endpoint='http://en.wikipedia.org/w/api.php'
    pageid=54458

    result = wikirectify.lang_links(endpoint,pageid)
    expected = ['http://es.wikipedia.org/wiki/Expresi%C3%B3n_S',
            'http://fi.wikipedia.org/wiki/S-lauseke',
            'http://fr.wikipedia.org/wiki/S-expression',
            'http://it.wikipedia.org/wiki/S-expression',
            'http://ja.wikipedia.org/wiki/S%E5%BC%8F',
            'http://ko.wikipedia.org/wiki/S-%ED%91%9C%ED%98%84%EC%8B%9D',
            'http://ru.wikipedia.org/wiki/S-%D0%B2%D1%8B%D1%80%D0%B0%D0%B6%'\
                    'D0%B5%D0%BD%D0%B8%D0%B5',
            'http://zh.wikipedia.org/wiki/S-%E8%A1%A8%E8%BE%BE%E5%BC%8F',
            'http://en.wikipedia.org/wiki/S-expression']

    assert result == expected
    return

def test_full_url():
    """
    Must return the full url of a page given the pageid.
    """

    endpoint='http://en.wikipedia.org/w/api.php'
    pageid=54458

    result = wikirectify.full_url(endpoint,pageid)
    expected = 'http://en.wikipedia.org/wiki/S-expression'
    assert result == expected

    return

def test_wiki_api_host():
    """
    Must return the api endpoint url corresponding to the given table name.
    """
    table_name = 'coord_simplewiki'
    expected = 'http://simple.wikipedia.org/w/api.php'

    assert expected == wikirectify.wiki_api_host(table_name)

    return

def test_wiki_title():
    """Must return the title of a wikipedia url"""
    wiki = "http://en.wikipedia.org/wiki/Montreal"
    expected = "Montreal"

    assert expected == wikirectify.wiki_title(wiki)
    return


def test_lang_code():
    """
    Must return the language code found in the table_name.
    """

    names = ['coord_enwiki','coord_frwiki','coord_ruwiki', 'coord_simplewiki']
    expecteds = ['en','fr','ru','simple']

    names_expecteds = zip(names,expecteds)

    for n,e in names_expecteds:
        assert e == wikirectify.lang_code(n)

    return

def test_geocoord_present():
    """
    Must return a tuple containing the lat and lon of the wiki when they are
    present.
    """
    wiki = 'http://en.wikipedia.org/wiki/Montreal'
    expected = (45.5,-73.5667)

    assert expected == wikirectify.geocoords(wiki)
    return

def test_gecoord_not_present():
    """
    must return None when the article contains no coordinates.
    """

    wiki = 'http://en.wikipedia.org/wiki/S-expression'
    expected = None

    assert expected == wikirectify.geocoords(wiki)
    return

def test_wiki_api_host_url():
    """
    must return the url endpoint of the corresponding wiki article.

    """
    couples = [
    ('http://en.wikipedia.org/wiki/Montreal',
        'http://en.wikipedia.org/w/api.php'),
    ('http://ru.wikipedia.org/wiki/%D0%9C%D0%BE%D0%BD%D1%80%D0%B5%D0%B0%D0%B'\
            'B%D1%8C', 'http://ru.wikipedia.org/w/api.php')
    ]

    for i,e in couples:
        assert e == wikirectify.wiki_api_host_url(i)

    return

def test_is_probable_no():
    """
    Must return False when a point is improbable
    """

    p = (7,8)
    mean_lats = 1
    mean_lons = 2
    sigma_lats = 1
    sigma_lons = 0.8

    assert not wikirectify.is_probable(p,mean_lats,mean_lons,sigma_lats,sigma_lons)
    return

def test_is_probable_yes():
    """
    Must return True when a point is probable
    """

    p = (8,9)
    mean_lats = 7.5
    mean_lons = 8.8
    sigma_lats = 1
    sigma_lons = 1

    assert wikirectify.is_probable(p,mean_lats, mean_lons, sigma_lats,sigma_lons)
    return


