from flask import jsonify as _jsonify
from roomiez_server.config import ErrorCode as _ErrorCode


def _retval(code, result=None):
    d = {
        'success': code == _ErrorCode.Success,
        'code': code.value
    }
    if result is not None:
        d['result'] = result
    return _jsonify(d)


def success(result):
    return _retval(_ErrorCode.Success, result)


def paginate_result(query, itemMap, page=1):
    pagination = query.paginate(page=page, per_page=50, max_per_page=100, error_out=False)
    return {
        'items': [itemMap(item) for item in pagination.items],
        'has_prev_page': pagination.has_prev,
        'has_next_page': pagination.has_next,
        'current_page': pagination.page,
        'total_pages': pagination.pages,
        'total_items': pagination.total,
    }


def paginate(query, itemMap, page=1):
    results = paginate_result(query, itemMap, page=page)
    return success(results)


def server_error():
    return _retval(_ErrorCode.UnknownError), 500


def not_found():
    return _retval(_ErrorCode.NotFound), 404


def bad_request(code, result=None):
    return _retval(code, result), 400


def unauthorized():
    return _retval(_ErrorCode.UnauthorizedAccess), 401


def get_post_data():
    """
    Gets the post data from supported Content-Types
    Returns a tuple
        Value 0:
        A bool flag representing if Content-Type was included
        Value 1:
        A dictionary of post data, or error response if Content-Type is unsupported
    """
    from flask import request
    contentType = request.content_type
    if contentType is None:
        return False, bad_request(_ErrorCode.NoContentType)

    r = None
    if contentType == 'application/json' or contentType == 'application/json; charset=utf-8':
        r = (True, request.json)
    elif contentType == 'application/x-www-form-urlencoded':
        d = dict(request.form)
        # Flatten the list to single values
        for key in d.keys():
            val = d[key]
            if len(val) == 1:
                d[key] = val[0]
        r = (True, d)
    else:
        return False, bad_request(_ErrorCode.InvalidContentType)
    return r
