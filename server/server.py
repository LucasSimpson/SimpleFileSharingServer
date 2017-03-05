import os
import re

from base import BaseConnection, BaseServer


class Lab3ServerConnectionHandler(BaseConnection):
    """Lab 3 Server Connection Handler."""

    SHARED_FOLDER = './server/shared_folder/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commands = {
            r'^LIST$': self.list,
            r'^GET-(?P<filename>.+)$': self.get,
            r'^PUT-(?P<filename>[^\s]+)\n(?P<contents>(.|\n)*)$': self.put
        }

    def handle_connection(self, conn, addr, *args, **kwargs):
        """Handle a client connection."""

        self.socket = conn
        self.run()
        self.close()

    def run(self):
        """Main Receive Loop."""

        while True:

            # receive message
            message = self.pull()

            # Exit inf loop if message is None (|disconnect)
            if not message:
                break

            # check commands for regex match
            handler = None
            for cmd in self.commands:
                match = re.match(cmd, message)

                if match:
                    handler = self.commands[cmd]
                    break

            # get response to send back from method, and send it back
            response = ''
            try:
                response = handler(**match.groupdict())

            except Exception as e:
                print(f'Error: {e}')
                response = str(e)

            finally:
                self.push(response)

        print(f'{self}: Client disconnected.')

    def list(self):
        """Returns a list of files in the sharing directory."""

        result = ''
        for filename in os.listdir(self.SHARED_FOLDER):
            result += f'{filename}\n'

        return result [:-1]  # drop last \n

    def get(self, filename):
        """Returns contents of file with name filename"""

        with open(f'{self.SHARED_FOLDER}{filename}', 'r') as file:
            return file.read()

    def put(self, filename, contents):
        """Saves file with name filename of contents contents to sharing directory. Returns ACK on success"""

        with open(f'{self.SHARED_FOLDER}{filename}', 'w') as file:
            file.write(contents)

        return 'ACK'


class Lab3Server(BaseServer):
    """Server class for coe4DN4 lab 3."""

    CONNECTION_KLASS = Lab3ServerConnectionHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print('Current files on servers shared directory:')
        for filename in os.listdir(self.CONNECTION_KLASS.SHARED_FOLDER):
            print(f'\t{filename}')


def run_server():
    s = Lab3Server()
    s.listen()

