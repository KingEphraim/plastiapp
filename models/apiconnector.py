import requests

def send_api_request(method="POST", url=None, headers=None, jsonBody=None, params=None):
    try:
        print(url)
        # Ensure the method is uppercase (in case it's provided in lowercase)
        method = method.upper()

        # Perform the API call based on the HTTP method
        if method == "POST":
            response = requests.post(url, headers=headers, json=jsonBody, params=params)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=jsonBody, params=params)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Check for successful response (status code 200-299)
        try:
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException:
            pass  # Catch the exception but continue to attempt to return the response

        # Return the response JSON if available, else the text
        try:
            return response.json()
        except ValueError:
            return response.text  # Return raw text if JSON is not available

    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.TooManyRedirects:
        return {"error": "Too many redirects"}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
