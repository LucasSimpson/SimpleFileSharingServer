import argparse

from client.client import run_client
from server.server import run_server


if __name__ == '__main__':
    roles = {'client': run_client,'server': run_server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles,
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()
