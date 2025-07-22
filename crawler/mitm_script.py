# -*- coding: utf-8 -*-
import json
import threading
from mitmproxy import http
from urllib.parse import urlparse, parse_qs

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

class MitmProxyHandler:
    def __init__(self, save_path: str, username: str, blacklist: list = None):
        self.is_data_captured = False
        self.request_url = None
        self.username = username
        self.save_path = save_path
        self.request_details = None
        self.response_details = None
        self.lock = threading.Lock()
        self.blacklist = blacklist if blacklist is not None else []

    def handle_request(self, flow: http.HTTPFlow) -> None:
        """Handle the incoming request and determine if it should be captured."""
        self.request_url = flow.request.pretty_url
        domain = urlparse(self.request_url).netloc
        for blacklist in self.blacklist:
            if blacklist in domain:
                self.is_data_captured = False
                return

        if not self.is_static_file(self.request_url):
            try:
                body = flow.request.content.decode('utf-8')
            except Exception as e:
                body = flow.request.content.hex()
            self.request_details = {
                "url": flow.request.pretty_url,
                "method": flow.request.method,
                "headers": dict(flow.request.headers),
                "body": body
            }
            self.is_data_captured = True
        else:
            self.is_data_captured = False

    def handle_response(self, flow: http.HTTPFlow) -> None:
        """Handle the response and save the request and response data if necessary."""
        if self.is_data_captured and self.is_success_response(flow.response.status_code):
            try:
                body = flow.response.content.decode('utf-8')
            except Exception as e:
                body = flow.response.content.hex()
            self.response_details = {
                "url": self.request_url,
                "headers": dict(flow.response.headers),
                "body": body
            }
            with self.lock:
                self.save_data()

    def save_data(self) -> None:
        """Save the request and response data to a file, organized by domain and username."""
        if self.request_details and self.response_details and self.username:
            data_to_save = {
                "request": self.request_details,
                "response": self.response_details
            }
            # Load existing data from file if it exists
            try:
                with open(self.save_path, "r") as file:
                    self.users_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                self.users_data = {}
            # Extract domain from URL
            domain = urlparse(self.request_url).netloc
            # Initialize domain data if not exists
            if domain not in self.users_data:
                self.users_data[domain] = {}
            # Append data to the user's data or create new user data if not exists
            if self.username not in self.users_data[domain]:
                self.users_data[domain][self.username] = []
            self.users_data[domain][self.username].append(data_to_save)
            # Save the updated dictionary back to the file
            with open(self.save_path, "w") as file:
                json.dump(self.users_data, file, indent=4)
            print(f"{BLUE}[>] request and response data for user {self.username} at domain {domain} has been saved...{RESET}")
            # Clear data to prepare for the next request and response
            self.request_details = None
            self.response_details = None
            self.is_data_captured = False

    def is_static_file(self, url: str) -> bool:
        """Check if the URL is a static file."""
        static_file_extensions = [
            '.js', '.css', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp',
            '.tif', '.swf', '.txt', '.svg', '.woff', '.ttf', '.eot', '.otf',
            '.woff2', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.flac',
            '.ovi', '.exe', '.sh', '.msi'
        ]
        return urlparse(url).path.endswith(tuple(static_file_extensions))

    def is_success_response(self, status_code: int) -> bool:
        """Determine if the response status code indicates a successful response."""
        return 200 <= status_code < 300

# Create MitmProxyHandler instance
save_path = "output.json"
user = "324070309110"
blacklist = ["googleapis.com", "gvt1-cn.com"]
mitm_handler = MitmProxyHandler(save_path=save_path, username=user, blacklist=blacklist)

# Mitmproxy hook functions
def request(flow: http.HTTPFlow) -> None:
    mitm_handler.handle_request(flow)

def response(flow: http.HTTPFlow) -> None:
    mitm_handler.handle_response(flow)


