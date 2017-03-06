from base import BaseClient


class Lab3Client(BaseClient):
    """Client for connecting to the file sharing server."""

    PORT = 30001
    TIMEOUT = 5

    def list(self):
        """Returns a list of all files on the remote server."""

        self.push(f'LIST')
        filenames = self.pull().split('\n')

        return filenames

    def get(self, filename):
        """Gets file contents with name filename from the remote server."""

        self.push(f'GET-{filename}')
        file_contents = self.pull()
        return file_contents

    def put(self, filename, file_contents):
        """Uploads file with name filename to the remote server."""

        self.push(f'PUT-{filename}\n{file_contents}')

        response = self.pull()
        if response != 'ACK':
            raise Exception(response)

    def bye(self):
        """Closes the connection."""

        self.push('BYE')
        self.close()


if __name__ == '__main__':
    c = Lab3Client()
    c.connect()
