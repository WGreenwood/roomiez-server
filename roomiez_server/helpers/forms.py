def requires_form_data(method=None, fields=None, customValidators=None):
    from functools import wraps, partial
    from roomiez_server.helpers import api, validation
    from roomiez_server.config import ErrorCode

    if method is None:
        return partial(requires_form_data, fields=fields, customValidators=customValidators)

    @wraps(method)
    def get_form(*args, **kwargs):
        isOk, data = api.get_post_data()
        if not isOk: return data  # noqa:E701

        code, results = validation.basic_form(fields, data, customValidators)
        if code is not ErrorCode.Success:
            return api.bad_request(code, results)

        return method(formData=results, *args, **kwargs)
    return get_form
