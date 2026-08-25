import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from typing import Optional


def is_url_resolvable(url: str, timeout_seconds: float = 5.0) -> bool:
    """
    Checks if a given URL is resolvable and accessible via HTTP/HTTPS.

    This function performs a lightweight HEAD request (which asks for the
    headers only, reducing bandwidth compared to a full GET) and checks
    if the response status code indicates success (2xx).

    Parameters:
    - url (str): The URL to test (must include http:// or https://).
    - timeout_seconds (float): The maximum time in seconds to wait for a
      response before timing out.

    Returns:
    - bool: True if the URL is accessible and returns a 2xx status code,
            False otherwise.
    """

    # Ensure the URL is valid, as requests might struggle with malformed ones
    if not url.startswith(('http://', 'https://')):
        print(f"Error: URL '{url}' is missing the 'http://' or 'https://' prefix.")
        return False

    try:
        # Use HEAD request for efficiency, as we only need the connection confirmation.
        # verify=True ensures SSL certificates are checked (standard security).
        response = requests.head(url, timeout=timeout_seconds, allow_redirects=True)

        # A status code in the 200s (e.g., 200 OK, 204 No Content) means success.
        # We also treat redirects (3xx) as resolvable if allow_redirects=True.
        # response.ok is a convenience property for status_code < 400
        if response.ok:
            print(f"Success: {url} resolved successfully (Status: {response.status_code}).")
            return True
        else:
            # Handle client errors (4xx) and server errors (5xx)
            print(f"Failed: {url} returned non-success status code: {response.status_code}.")
            return False

    except Timeout:
        # Server is too slow or request took too long
        print(f"Error: Timeout occurred while trying to connect to {url}.")
        return False

    except ConnectionError:
        # DNS failure, server refused connection, or network unreachable
        print(f"Error: Connection failed. Could not resolve DNS or reach the server for {url}.")
        return False

    except RequestException as e:
        # Catches other request-related errors (e.g., invalid URL format, SSL errors)
        print(f"Error: An unexpected request error occurred for {url}: {e}")
        return False

    except Exception as e:
        # Catches any non-request related exceptions
        print(f"Error: An unexpected error occurred: {e}")
        return False


# --- Example Usage ---
if __name__ == "__main__":
    # 1. Resolvable and working URL
    working_url = "https://www.kit.edu/"
    is_working = is_url_resolvable(working_url)
    print(f"Result for {working_url}: {is_working}\n")

    # 2. Non-existent domain (DNS failure or ConnectionError)
    bad_dns_url = "http://www.nonexistentdomainfortestonly12345.com/"
    is_bad_dns = is_url_resolvable(bad_dns_url)
    print(f"Result for {bad_dns_url}: {is_bad_dns}\n")

    # 3. Existing domain but slow/down service (Timeout)
    # Using a known site but with a very short timeout to simulate slowness
    timeout_url = "https://google.com/"
    is_timeout = is_url_resolvable(timeout_url, timeout_seconds=0.001)
    print(f"Result for {timeout_url} (short timeout): {is_timeout}\n")

    # 4. URL that returns an error status code (e.g., 404)
    # Note: This is still resolvable, but not accessible for content
    # We define "resolvable" here as 'can reach and get a 2xx status'
    error_url = "https://httpbin.org/status/404"
    is_error = is_url_resolvable(error_url)
    print(f"Result for {error_url}: {is_error}\n")
