import multiprocessing
from argparse import ArgumentParser

from client import HonClient
from manifest import ManifestParser


class HonParser:
    def __init__(self, os, arch):
        # example wac / mac / linux
        self.os = os
        # example i686
        self.arch = arch
        # self.poolsize = int(args.poolsize)
        self.base_url = 'http://masterserver.naeu.heroesofnewerth.com/'

    def main(self, version):
        # example 2.6.10, 4.10.
        self.version = version

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

        manifest_filename = 'manifest.xml.zip'
        manifest_response = _client.get_manifest(
            base_url='http://dl.heroesofnewerth.com/',  # must get from patcher_data response
            version=self.version,  # must get from patcher_data response
            filename=manifest_filename,
        )

        ManifestParser(os=self.os, arch=self.arch).parse(
            client=_client,
            manifest_file=manifest_response,
            base_url='http://dl.heroesofnewerth.com/',
        )

        print('\nDone, version: {version}'.format(version=self.version))

parser = ArgumentParser(description='Hon Client downloader')
parser.add_argument(
    '-sv',
    '--semver',
    dest='semver',
    help='download hon client version SEMVER',
    metavar='SEMVER',
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
parser.add_argument(
    '-l',
    '--version-list',
    dest='version_list',
    help='list of version to download',
    metavar='VERSION_LIST',
)

_args = parser.parse_args()

# manual logic for version/version_list arguments
if _args.version_list is None:
    if _args.semver is None:
        raise Exception('"semver" variable is required')

    HonParser(
        os=_args.os,
        arch=_args.arch,
    ).main(
        version=_args.semver
    )
else:
    versions = _args.version_list.split(',')
    poolsize = len(versions) if len(versions) < 8 else 8
    pool = multiprocessing.Pool(poolsize)
    # defaults to windows and i686
    results = pool.map(
        HonParser(
            os=_args.os,
            arch=_args.arch
        ).main,
        versions
    )
