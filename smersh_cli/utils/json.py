from .case import snake_case


def extract_id_from_url(url):
    return url.split('/')[-1]


def convert_dict_keys_case(data, case_function):
    converted = {}

    for k, v in data.items():
        if type(v) == dict:
            v = convert_dict_keys_case(v, case_function)

        converted[case_function(k)] = v

    return converted


def is_collection(data):
    return ('@type' in data) and (data['@type'] == 'hydra:Collection')


def clean_ldjson(data):
    data_type = type(data)

    if data_type == list:
        cleaned = []

        for e in data:
            cleaned.append(clean_ldjson(e))

        return cleaned

    elif data_type == dict:
        if is_collection(data):
            return clean_ldjson(data['hydra:member'])

        if ('id' not in data) and ('@id' not in data):
            return data

        id_ = data['id' if 'id' in data else '@id']

        if type(id_) == int:
            id_ = str(id_)
        else:
            id_ = extract_id_from_url(id_)

        cleaned = {
            'id': id_
        }

        for k, v in data.items():
            if (k[0] != '@') and (k != 'id'):
                cleaned[snake_case(k)] = clean_ldjson(v)

        return cleaned

    return data


def wrap_id(data):
    if type(data) == list:
        return [{'id': e} for e in data]

    return {'id': data}


def wrap_id_dict(data, keys):
    # TODO: This function does not support object nesting
    wrapped = {}

    for k, v in data.items():
        wrapped[k] = wrap_id(v) if k in keys else v

    return wrapped


def clean_none_keys(data):
    cleaned = {}

    for k, v in data.items():
        if v is not None:
            cleaned[k] = v

    return cleaned
