import socket
import threading


class NetworkModule:
    """Basic network module. Defines constants and baseline TCP-oriented methods."""

    HOSTNAME = socket.gethostname()
    PORT = 30001

    ENCODING = 'utf-8'
    PACKET_SIZE = 1024

    def __init__(self, socket_=None):
        self.socket = socket_ if socket_ else socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def push(self, message):
        """Send message through the connection."""

        size = socket.htonl(len(message))
        mesg_b = message.encode(self.ENCODING)
        final_msg = bytes([
            size >> 24 & 0xFF,
            size >> 16 & 0xFF,
            size >> 8 & 0xFF,
            size & 0xFF,
        ]) + mesg_b

        self.socket.sendall(final_msg)

    def _recv(self, num_bytes):
        """Receive a specific number of bytes."""

        result = b''
        num_received = 0
        while num_received < num_bytes:
            chunk = self.socket.recv(min(num_bytes - num_received, self.PACKET_SIZE))
            if not chunk:
                return None

            result += chunk
            num_received += len(chunk)

        return result

    def pull(self):
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

        return enc_msg.decode(self.ENCODING)

    def close(self):
        """Closes a connection."""

        self.socket.close()
        self.__init__()


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
    CONNECTION_KLASS = BaseConnection

    def __init__(self, socket_=None):
        super().__init__(socket_)

    def listen(self):
        """Start listening for, and process, connections on HOSTNAME:PORT"""

        self.socket.bind((self.HOSTNAME, self.PORT))
        self.socket.listen(self.BACKLOG)
        print(f'{self}: Listening on port {self.PORT}...')

        while True:
            try:
                conn, addr = self.socket.accept()
                print(f'{self}: {conn} from {addr} connection accepted.')
                threading.Thread(target=self.CONNECTION_KLASS().handle_connection, args=(conn, addr)).start()

            except Exception as e:
                print(e)






