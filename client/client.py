import os
import re
import sys

from client.sd_client_connection import Lab3ServiceDiscoveryClient
from .client_connection import Lab3Client


class Client:
    SHARED_FOLDER = './client/shared_folder/'

    def __init__(self):
        self.connection = Lab3Client()
        self.sd_connection = Lab3ServiceDiscoveryClient()
        self.connected_to = None

        self.commands = {
            r'scan': self.scan,
            r'connect (?P<addr>[^\s]+) (?P<port>[0-9]+)': self.connect,
            r'llist': self.llist,
            r'rlist': self.rlist,
            r'put (?P<filename>[^\s]+)': self.put,
            r'get (?P<filename>[^\s]+)': self.get,
            r'bye': self.bye,

            r'help': self.help,
            r'exit': self.exit,
        }

    def get_command_match(self, text):
        """Matches text with commands and returns (match object, method)."""

        for cmd in self.commands:
            match = re.match(cmd, text)
            if match:
                return match, self.commands[cmd]
        return None, None

    def start(self):
        """Enter REPL."""

        while True:
            cmd_text = input(f'\n{"(" + self.connected_to + ") " if self.connected_to else ""}Enter Command: ')
            match, method = self.get_command_match(cmd_text)
            if match:
                try:
                    # call method with args
                    method(**match.groupdict())
                except Exception as e:
                    print(e)

            else:
                print('Invalid command')

    def scan(self):
        """Scans network and prints out valid connections."""

        services = self.sd_connection.find_all_services()

        if not services:
            print('No services found :(')
            return

        print('Services found:')
        for service in services:
            print(f'\t{service[1][0]}: {service[0]}')

    def connect(self, addr, port):
        """Connect to remote server on addr:port."""

        if self.connected_to:
            print(f'You\'re already connected to {self.connected_to}!')
            print('Disconnect first with \'bye\'')
            return

        try:
            self.connection.connect((addr, int(port)))
            self.connected_to = f'{addr}:{port}'
            print(f'Successfully connected to {self.connected_to}')
        except Exception as e:
            print(f'Error connecting: {e}')

    def llist(self):
        """Prints out a directory listing of files in the local file sharing directory."""

        filenames = os.listdir(self.SHARED_FOLDER)

        print('Local filepaths:')
        for filename in filenames:
            print(f'\t{filename}')

    def rlist(self):
        """Prints out a directory listing of files on the remote file sharing directory."""

        if not self.connected_to:
            print('You aren\'t connected to anyone!')
            print('Connect first with \'connect <hostname> <port>\'')
            return

        filenames = self.connection.list()

        print('Remote filepaths:')
        for filename in filenames:
            print(f'\t{filename}')

    def get(self, filename):
        """Download and saves a copy of the file with name filename from remote server."""

        if not self.connected_to:
            print('You aren\'t connected to anyone!')
            print('Connect first with \'connect <hostname> <port>\'')
            return

        try:
            file_contents = self.connection.get(filename)

            with open(f'{self.SHARED_FOLDER}{filename}', 'w') as file:
                file.write(file_contents)

            print(f'{filename} successfully downloaded')

        except Exception as e:
            print(f'Error downloading: {e}')

    def put(self, filename):
        """Uploads file with name filename to remote server."""

        if not self.connected_to:
            print('You aren\'t connected to anyone!')
            print('Connect first with \'connect <hostname> <port>\'')
            return

        try:

            with open(f'{self.SHARED_FOLDER}{filename}', 'r') as file:
                file_contents = file.read()

            self.connection.put(filename, file_contents)

            print(f'{filename} successfully uploaded')

        except Exception as e:
            print(f'Error uploading: {e}')

    def bye(self):
        """Closes the current connection."""

        if not self.connected_to:
            print('You aren\'t connected to anyone!')
            print('Connect first with \'connect <hostname> <port>\'')
            return

        self.connection.bye()
        self.connected_to = None
        print('Disconected')

    def help(self):
        """Shows help information."""

        print(f'Valid commands are:')
        for key in self.commands.keys():
            print(f'\t{key}')

    def exit(self):
        sys.exit(0)


def run_client():
    c = Client()
    c.start()
