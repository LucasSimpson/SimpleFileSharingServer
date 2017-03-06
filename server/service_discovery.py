from base.base import BaseUDPServer


class Lab3DiscoveryServer(BaseUDPServer):
    """Server class that listens for SDP."""

    HOSTNAME = '255.255.255.255'
    PORT = 30000

    def handle_packet(self, msg, addr_port):
        if msg == 'SERVICE DISCOVERY':
            print(f'SDP from {addr_port[0]}:{addr_port[1]}')
            return 'Dan/Matt/Lucas\'s file sharing service ¯\_(ツ)_/¯'
