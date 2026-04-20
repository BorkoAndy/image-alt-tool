import json

def handler(request):
    return {
        "statusCode": 410,
        "body": json.dumps({"error": "This endpoint has been deprecated and removed. Please use /api/v1/analyze instead."}),
        "headers": {"Content-Type": "application/json"}
    }
