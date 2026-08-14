"""Custom DRF exception handler - consistent error format."""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        if isinstance(data, dict) and "detail" in data and len(data) == 1:
            message = str(data["detail"])
            errors = None
        else:
            message = _first_message(data)
            errors = data

        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
        }
    return response


def _first_message(data):
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, (list, tuple)):
                if value:
                    return str(value[0])
            elif isinstance(value, str):
                return value
        return "So'rov noto'g'ri."
    if isinstance(data, (list, tuple)):
        return str(data[0]) if data else "So'rov noto'g'ri."
    return str(data)