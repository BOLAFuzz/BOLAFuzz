import json


def generate_signature(request):
    request_data = {
        "url": request["url"],
        "method": request["method"],
        "headers": dict(sorted(request["headers"].items())),
        "body": request["body"],
        "params": request["params"]
    }
    return json.dumps(request_data, sort_keys=True).encode('utf-8')
