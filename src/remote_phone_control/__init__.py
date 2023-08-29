from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading


__author__ = '139928764+p4irin@users.noreply.github.com'
__version__ = '0.1.0'


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        """
        Sets appropriate event _Event objects, when a snom fires an event,
        i.e. when a snom makes a GET request to an 'action url'. These are
        defined in a WebServer and instantiated in an ActionServer.
        The ActionServer's calling thread, i.e a Snom, Must issue a wait()
        to wait for an event to occur.
        """

        self.send_response(200)
        self.end_headers()

        path = urlparse(self.path).path
        if not path == '/event': return

        qs = parse_qs(urlparse(self.path).query)

        if qs['event'][0] == 'incoming':
            self.server.event_incoming_call.set()
            self.server.remote_caller = qs['remote'][0]

        if qs['event'][0] == 'disconnected':
            self.server.event_disconnect.set()
            self.server.remote_caller = qs['remote'][0]

        if qs['event'][0] == 'connected':
            self.server.event_connect.set()
            self.server.remote_caller = qs['remote'][0]

    def log_message(self, fmt, *args):
        """
        Override parent's log_message method to suppress logging messages
        on the console. Rename/comment this method to undo this for
        debugging.
        """
        return


class WebServer(HTTPServer):
    """
    Define snom events and serve an HTTP server to handle them.
    """

    remote_caller = None
    remote_display = None
    event_incoming_call = None
    event_disconnect = None
    event_connect = None


class ActionServer(threading.Thread):
    """
    Setup a WebServer to handle snom 'action urls' and run it in its
    own thread.
    """

    def __init__(self, port: int):
        """
        Listen on port for events of a specific snom.
        port Must be tied to a specific snom and used when configuring
        a snom's 'action urls'.
        """

        threading.Thread.__init__(self)
        self.port = port
        self.server = WebServer(('', port), GetHandler)
        self.server.event_disconnect = threading.Event()
        self.server.event_connect = threading.Event()
        self.server.event_incoming_call = threading.Event()

    def run(self) -> None:
        self.server.serve_forever()

    def stop(self) -> None:
        """
        You MUST call this from where you instantiated a Snom
        :return:
        """
        self.server.shutdown()
        # Force socket close to avoid address already in use exceptions
        self.server.socket.close()
        # Commented out cause results in ResourceWarning: unclosed.... in python-3.6.7
        # del self.server