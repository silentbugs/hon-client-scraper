from argparse import ArgumentParser

from client import HonClient
from manifest import ManifestParser


class HonParser:
    def __init__(self, args):
        # example 2.6.10, 4.10.
        self.version = args.semver
        # example wac / mac / linux
        self.os = args.os
        # example i686
        self.arch = args.arch
        # self.poolsize = int(args.poolsize)
        self.base_url = 'http://masterserver.naeu.heroesofnewerth.com/'

    def get_client_url(self, arch):
        default = 'http://dl.heroesofnewerth.com/'

        urls = {
            'i686': default,
            'x86_64': 'https://cdn.naeu.patch.heroesofnewerth.com/'
        }

        if arch in urls.keys():
            return urls[arch]

        return default

    def main(self):
        _client = HonClient(
            base_url=self.base_url,
            os=self.os,
            arch=self.arch,
            version=self.version,
        )

        patcher_data = _client.patcher(
            version='0.0.0.0',
            cookie=''  # 32 bytes
        )


        if not patcher_data.ok():
            raise Exception('Unable to get patcher data.')

        client_url = self.get_client_url(self.arch)

        manifest_filename = 'manifest.xml.zip'
        manifest_response = _client.get_manifest(
            base_url=client_url,  # must get from patcher_data response
            version=self.version,  # must get from patcher_data response
            filename=manifest_filename,
        )

        ManifestParser(os=self.os, arch=self.arch).parse(
            client=_client,
            manifest_file=manifest_response,
            base_url=client_url,
        )

        print(f'\nDone, version: {self.version}')

parser = ArgumentParser(description='Hon Client downloader')
parser.add_argument(
    '-sv',
    '--semver',
    dest='semver',
    help='download hon client version SEMVER',
    metavar='SEMVER',
    required=True,
)

parser.add_argument(
    '-o',
    '--os',
    dest='os',
    help='hon client operating system',
    metavar='OS',
    required=True,
)

parser.add_argument(
    '-a',
    '--arch',
    dest='arch',
    help='hon client architecture',
    metavar='ARCH',
    required=True,
)

_args = parser.parse_args()

HonParser(_args).main()
