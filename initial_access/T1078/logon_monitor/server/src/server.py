import json
import time
import queue
import datetime
import threading
from tinydb import TinyDB, Query
from http.server import HTTPServer, BaseHTTPRequestHandler

# local imports
import utils
import fill_info

# queue for json strings (logon and logoff events)
q = queue.Queue()


def fill_all_info(event):
    json_event = json.loads(event)
    event_object = fill_info.Event(json_event)

    # see example_json.json
    fill_info.fill_statistics(event_object)

# consumer gets events from queue and process it
def consumer():
    while True:
        try:
            # get our event from queue
            event = q.get(timeout=1)
            if event is None:
                break
            # out main function for processing events
            fill_all_info(event)
            # mark as processed event
            q.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Consumer: An error occurred: {e}")
            break

# simple http server what listens on /api/events 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/events':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            json_event = body.decode('utf-8')
            # put event in queue
            q.put(json_event)
        else:
            self.end_headers()

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=443):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("server started...")
    httpd.serve_forever()

if __name__ == '__main__':
    # thread for getting and processing events
    thread = threading.Thread(target=consumer)
    thread.start()

    # thread for catching and putting events
    run()