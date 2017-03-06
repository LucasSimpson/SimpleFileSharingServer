import socket

from base import BaseClient
from base.mixins import UDPMixin


class Lab3ServiceDiscoveryClient(UDPMixin, BaseClient):
    """Client for connecting the service discover server."""

    PORT = 30000
    TIMEOUT = 2

    def build_socket(self):
        """Enable broadcasting."""

        socket_ = super().build_socket()
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        return socket_

    def find_all_services(self):
        """Returns a list of available services."""

        self.push('SERVICE DISCOVERY', ('255.255.255.255', self.PORT))
        print(f'Listening for SDP response ({self.TIMEOUT}s)...')

        services = list()
        while True:

            try:
                services.append(self.pull())

            except socket.timeout:
                break

        return services
