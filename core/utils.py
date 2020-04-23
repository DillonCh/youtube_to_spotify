class HttpError(Exception):
    pass


def get_json(path):
    import json
    with open(path) as my_file:
        data = json.load(my_file)
    return data
