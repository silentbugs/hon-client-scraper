import os
import xml.etree.ElementTree as ET
import zipfile

from progress.bar import Bar

from utils import FileUtil, SemverUtil


class ManifestParser:
    def __init__(self, os, arch):
        self.os = os
        self.arch = arch
        self.data_dir = 'data'

    def extract(self, response, manifest_filename, version):
        # ensure data dir exists
        data_path = os.path.join(
            self.data_dir,
            self.os,
            self.arch,
            version,
        )
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        filepath = os.path.join(data_path, manifest_filename)
        filepath = FileUtil.save_file(
            filepath=filepath,
            data=response.content,
        )

        with zipfile.ZipFile(filepath, 'r') as zip_file:
            zip_file.extractall(data_path)

        return os.path.join(data_path, 'manifest.xml')

    def parse_child(self, child):
        if child.tag == 'file':
            path = '{_path}.zip'.format(_path=child.attrib['path'])
            version = child.attrib['version']
            # zipsize = child.attrib['zipsize']
            # size = child.attrib['size']
            # checksum = child.attrib['checksum']

            try:
                self.bar.next()

                full_path = os.path.join(
                    self.data_dir,
                    self.os,
                    self.arch,
                    SemverUtil(self._version).pretty(),
                    os.path.dirname(path),
                )
                file_name = FileUtil.path_leaf(path)
                filepath = os.path.join(full_path, file_name)

                # skip existing files
                if os.path.exists(filepath):
                    return filepath

                os.makedirs(full_path, exist_ok=True)

                response = self.client.get_file(
                    path=path,
                    os=self._os,
                    arch=self._arch,
                    version=version,
                )

                filepath = FileUtil.save_file(
                    filepath=filepath,
                    data=response.content,
                )
            except FileNotFoundError as e:
                print('\n')
                print(e)
            except Exception as e:
                print('\n')
                print(e)

            return filepath

    def parse(
        self,
        manifest_file,
        client=None,
        base_url=None,
        check_files=False,
    ):
        if client is None and not check_files:
            raise Exception('Either pass a client or check_files=True')

        # prepare client
        if client is not None:
            client.base_url = base_url
            self.client = client

        # prepare XML
        xml = ET.parse(manifest_file)
        root = xml.getroot()

        if root.tag == 'manifest':
            self._os = root.attrib['os']
            self._arch = root.attrib['arch']
            self._version = root.attrib['version']

            total_items = len(root)

            bar_messsage = 'Downloading HoN client {v}'.format(v=self._version)
            self.bar = Bar(bar_messsage, max=total_items)
            for child in root:
                self.parse_child(child)
