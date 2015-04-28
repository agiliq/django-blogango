import urllib
import urllib2
from django.utils import json
import views

site = 'blogango.com'


def search(request):
    query_term = ""
    for term in request.GET['q']:
        query_term += term
    results = \
        get_search_results(
            'YLPjx2rV34F4hXcTnJYqYJUj9tANeqax76Ip2vADl9kKuByRNHgC4qafbATFoQ',
            query_term, site=site)
    print [result['Url'] for result in results]
    payload = {'results': results}
    return views.render('search.html', request, payload)


def get_search_results(appid, query, region='us', type='all',
                       results=10, start=0, format='any',
                       adult_ok="", similar_ok="", language="",
                       country="", site="", subscription="", license=''):
    base_url = u'http://search.yahooapis.com/WebSearchService/V1/webSearch?'
    params = locals()
    result = _query_yahoo(base_url, params)
    return result['ResultSet']['Result']


def _query_yahoo(base_url, params):
    params['output'] = 'json'
    payload = urllib.urlencode(params)
    url = base_url + payload
    print url
    response = urllib2.urlopen(url)
    result = json.load(response)
    return result
