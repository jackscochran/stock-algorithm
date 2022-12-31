import requests
from ..data import fmp_cache

API_KEY = ''

def get_response(url):

    # check if url exists
    response = fmp_cache.Response.objects(url=url).first()
    if response is not None:
        return response.results

    # make api call
    results = requests.get(f'https://fmpcloud.io/api/{url}&apikey={API_KEY}').json()

    # check if valid results
    if len(results)==0:
        return None

    # save response
    response = fmp_cache.Response(
        url=url,
        results=results
    )
    try:
        response.save()
    except OverflowError:
        pass

    return results

