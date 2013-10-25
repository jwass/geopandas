import webbrowser
import urllib

try:
    import github3
except ImportError:
    _HAS_GITHUB3 = False
else:
    _HAS_GITHUB3 = True

MAX_URL_LEN = 150e3  # Size threshold above which a gist is created
MAX_GITHUB_LEN = 10e6  # Max size for gists

def to_geojsonio(contents, gist=True, domain='http://geojson.io/'):
    """
    Send GeoJSON contents to http://geojson.io in a web browser to quickly
    plot them on a slippy map. If the contents are large, an anonymous gist
    will be created on Github.

    Parameters
    ----------
    contents : string
        String of GeoJSON to display
    gist : boolean, default True
        If the GeoJSON contents are too large to be embedded in the URL,
        this indicates whether a Github gist should be created.
    domain : string, default 'http://geojson.io/'
        The domain to use. Most likely run on localhost if not using the
        default option

    Returns
    -------
    url : str
        The geojson.io URL used to open the web browser. The URL can be
        re-used.

    http://geojson.io has serveral ways of getting data into the browser and
    ultimately onto a map. It allows directy upload of geospatial files or
    drag-and-drop. Additionally there is a URL API enabling other means that
    don't require browser interaction. The data can be embedded directly into
    the URL. The maximum size is limited by the maximum URL size browsers are
    willing to handle. Additionally a URL can be specified allowing the raw
    data in a Github Gist to be used. This function will try to embed GeoJSON
    data into the URL. If it is too large, it will create an anonymous gist on
    Github and use a corresponding URL telling geojson.io to fetch the data
    from Github.

    """
    url = geojsonio_url(contents, gist, domain)
    webbrowser.open(url)

    return url


def geojsonio_url(contents, gist=True, domain='http://geojson.io/'):
    """
    Returns the URL to open given the domain and contents

    If the contents are larger than 150kB, a gist will be created. Contents
    larger than 10MB will raise ValueError

    """
    if len(contents) <= MAX_URL_LEN:
        url = _data_url(domain, contents)
    elif gist and len(contents) <= MAX_GITHUB_LEN:
        gist = _create_gist(contents)
        url = _gist_url(domain, gist.id)
    else:
        raise ValueError('Contents are too large')

    return url


def _create_gist(contents, description='', filename='data.geojson'):
    """
    Create and return an anonymous gist with a single file and specified
    contents

    """
    if not _HAS_GITHUB3:
        raise ImportError('github3 not found. Please install it.')

    ghapi = github3.GitHub()
    files = {filename: {'content': contents}}
    gist = ghapi.create_gist(description, files)

    return gist


def _data_url(domain, contents):
    url = (domain + '#data=data:application/json,' +
           urllib.quote(contents))
    return url


def _gist_url(domain, gist_id):
    url = (domain + '#id=gist:/{}'.format(gist_id))
    return url
