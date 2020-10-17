import itertools

import flask.json as json
from roomiez_server.config import ErrorCode

CONTENT_TYPE = 'application/json'


def json_request(client, url, method='POST', data={}, headers={}):
    params = {
        'path': url,
        'method': method,
        'headers': headers,
        'data': json.dumps(data),
        'content_type': CONTENT_TYPE,
        'charset': 'utf-8'
    }
    res = client.open(**params)
    assert res.data is not None, 'Server returned no data'
    jsonText = res.data.decode('utf-8')
    jsonObj = json.loads(jsonText)
    assert 'code' in jsonObj, 'Server returned no error code'
    assert 'success' in jsonObj, 'Server returned no success flag'

    code = ErrorCode(jsonObj['code'])
    success = jsonObj['success']
    result = jsonObj['result'] if 'result' in jsonObj else None
    return code, success, result, res.status_code


def set_auth(jwt, headers=None):
    if headers is None:
        headers = {}
    headers['Authentication'] = 'Bearer {}'.format(jwt)
    return headers


def get_combinations(lst):
    results = []
    for i in range(1, len(lst) + 1):
        for combination in itertools.combinations(lst, i):
            results.append(combination)
    return results
def get_combinations_double(method, keys, values):  # noqa:E302
    results = []
    for keyCombo in get_combinations(keys):
        valueCombos = itertools.combinations(values, len(keyCombo))
        for valueCombo in valueCombos:
            results.append((method, dict(zip(keyCombo, valueCombo))))
    return results
