import socket


class UDPMixin:
    """Make connection UDP oriented instead of the default TCP."""

    PACKET_SIZE = 256

    def push(self, message, addr_port):
        """UDP push."""

        msg_b = message.encode(self.ENCODING)
        self.socket.sendto(msg_b, addr_port)

    def pull(self):
        """UDP Pull. Returns (message, (address, port))."""

        msg_b, addr_port = self.socket.recvfrom(self.PACKET_SIZE)
        return msg_b.decode(self.ENCODING), addr_port

    def build_socket(self):
        """Builds an IPv4 UDP socket."""

        socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_.settimeout(self.TIMEOUT)

        return socket_

    def prepare_socket(self):
        """Binds UDP socket. No listen() required for UDP."""

        self.socket.bind((self.HOSTNAME, self.PORT))
