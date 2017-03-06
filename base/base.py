import socket
import threading

from base.mixins import UDPMixin


def get_host_name():
    """This is a hack to get public IP address."""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    hostname = s.getsockname()[0]
    s.close()

    return hostname


class NetworkModule:
    """Basic network module. Defines constants and baseline TCP-oriented methods."""

    HOSTNAME = get_host_name()
    PORT = 30001

    ENCODING = 'utf-8'
    PACKET_SIZE = 1024

    TIMEOUT = None

    def __init__(self, socket_=None):
        self.socket = socket_ if socket_ else self.build_socket()

    def build_socket(self):
        """Build the socket. Can be overriden to use different types."""

        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_.settimeout(self.TIMEOUT)

        return socket_

    def push(self, message, encode=True):
        """Send message through the connection."""

        assert (type(message) is str if encode else type(message) is bytes)

        msg_b = message.encode(self.ENCODING) if encode else message

        size = socket.htonl(len(message))
        final_msg = bytes([
            size >> 24 & 0xFF,
            size >> 16 & 0xFF,
            size >> 8 & 0xFF,
            size & 0xFF,
        ]) + msg_b

        self.socket.sendall(final_msg)

    def _recv(self, num_bytes):
        """Receive a specific number of bytes."""

        result = b''
        num_received = 0
        while num_received < num_bytes:
            try:
                chunk = self.socket.recv(min(num_bytes - num_received, self.PACKET_SIZE))
            except OSError as e:
                return None  # client disconnected

            if not chunk:
                return None

            result += chunk
            num_received += len(chunk)

        return result

    def pull(self, decode=True):
        """Receive a message from the connection."""

        size_b = self._recv(4)
        if not size_b:
            return None

        size = socket.ntohl(
            (size_b[0] << 24) +
            (size_b[1] << 16) +
            (size_b[2] << 8) +
            (size_b[3])
        )

        enc_msg = self._recv(size)

        if not enc_msg:
            return None

        return enc_msg.decode(self.ENCODING) if decode else enc_msg

    def close(self):
        """Closes a connection."""

        self.socket.close()
        self.__init__()

    def __str__(self):
        return str(self.__class__)[8:-2]


class BaseConnection(NetworkModule):
    """Defines any client to a connection."""

    def __init__(self, socket_=None):
        super().__init__(socket_)

    def handle_connection(self, conn, addr, *args, **kwargs):
        """Connection is established, act on it."""

        raise NotImplemented(f'{self.__class__} has to override handle_connection().')


class BaseClient(BaseConnection):
    """Defines a client that will connect to a server."""

    def __init__(self):
        super().__init__(socket_=None)

    def connect(self, addr_port_tuple=None):
        location = addr_port_tuple if addr_port_tuple else (self.HOSTNAME, self.PORT)
        self.socket.connect(location)


class BaseServer(NetworkModule):
    """Defines a Server socket. Listens for connections, creates server-client instances, and repeats."""

    BACKLOG = 5
    CONNECTION_CLASS = BaseConnection

    def prepare_socket(self):
        """Prepare socket for listening."""

        self.socket.bind((self.HOSTNAME, self.PORT))
        self.socket.listen(self.BACKLOG)

    def listen(self):
        """Start listening for, and process, connections on HOSTNAME:PORT"""

        self.prepare_socket()
        print(f'{self}: Listening on {self.HOSTNAME}:{self.PORT}...')

        while True:
            try:
                conn, addr = self.socket.accept()
                print(f'{self}: Connection from {addr[0]} accepted on port {addr[1]}.')
                threading.Thread(target=self.CONNECTION_CLASS().handle_connection, args=(conn, addr)).start()

            except Exception as e:
                print(e)


class BaseUDPServer(UDPMixin, NetworkModule):
    """Defines a base server that handles UDP packets."""

    def listen(self):
        """Start listening and processing UDP packets."""

        self.prepare_socket()
        print(f'{self}: Listening on {self.HOSTNAME}:{self.PORT}')

        while True:
            try:
                msg, addr_port = self.pull()
                response = self.handle_packet(msg, addr_port)

                if response:
                    self.push(response, addr_port)

            except Exception as e:
                print(e)

    def handle_packet(self, msg, addr_port):
        """Handler method for handling a single UDP packet."""

        raise NotImplemented(f'{self.__class__} has to implement handle_packet(msg)')
