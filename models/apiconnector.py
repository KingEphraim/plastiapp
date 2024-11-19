import requests

def submit_request(url, method="POST", headers=None, data=None, json_data=None, params=None):
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            json=json_data,
            params=params
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()  # Return parsed JSON response
    except requests.exceptions.HTTPError as http_err:
        return {
            "error": "HTTP error occurred",
            "details": str(http_err),
            "status_code": response.status_code,
            "response_text": response.text
        }
    except requests.exceptions.ConnectionError as conn_err:
        return {
            "error": "Connection error occurred",
            "details": str(conn_err)
        }
    except requests.exceptions.Timeout as timeout_err:
        return {
            "error": "Request timed out",
            "details": str(timeout_err)
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": "An error occurred with the request",
            "details": str(req_err)
        }
