import wikirectify

def test_lang_links():
    """
    must return a list of the language links from a live wikipedia instance.
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
            'http://ru.wikipedia.org/wiki/S-%D0%B2%D1%8B%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5',
            'http://zh.wikipedia.org/wiki/S-%E8%A1%A8%E8%BE%BE%E5%BC%8F',
            'http://en.wikipedia.org/wiki/S-expression']

    assert result == expected
    return

def test_full_url():
    """
    must return the full url of a page given the pageid.
    """

    endpoint='http://en.wikipedia.org/w/api.php'
    pageid=54458

    result = wikirectify.full_url(endpoint,pageid)
    expected = 'http://en.wikipedia.org/wiki/S-expression'
    assert result == expected

    return

def test_wiki_api_host():
    """
    must return the api endpoint url corresponding to the given table name.
    """
    table_name = 'coord_simplewiki'
    expected = 'http://simple.wikipedia.org/w/api.php'

    assert expected == wikirectify.wiki_api_host(table_name)

    return

def test_lang_code():
    """
    must return the language code found in the table_name.
    """

    names = ['coord_enwiki','coord_frwiki','coord_ruwiki', 'coord_simplewiki']
    expecteds = ['en','fr','ru','simple']

    names_expecteds = zip(names,expecteds)

    for n,e in names_expecteds:
        assert e == wikirectify.lang_code(n)

    return
