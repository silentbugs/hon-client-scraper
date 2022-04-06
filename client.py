import requests

from urllib.parse import urljoin

from manifest import ManifestParser
from utils import SemverUtil


class BaseRequest:
    def serialize(self):
        items = self.__dict__
        the_items = []

        for item in items:
            item_data = '{key}={value}'.format(
                key=item,
                value=items[item]
            )
            the_items.append(item_data)

        serialized = '&'.join(the_items)

        return serialized


class BaseResponse:
    def deserialize(self, data):
        # need to custom deserialize/tokenize the data of type:
        #
        #
        # a:2:{
        #     i:0;:8: {
        #         s:7:"version";s:6:"4.10.1";
        #         s:2:"os";s:3:"wac";
        #         s:4:"arch";s:4:"i686";
        #         s:3:"url";s:30:"http://dl.heroesofnewerth.com/";
        #         s:4:"url2";s:33:"http://patch.heroesofnewerth.com/";
        #         s:14:"latest_version";s:6:"4.10.1";
        #         s:24:"latest_manifest_checksum";s:40:"e8e54bf5cd5dbe486b7f9c3166dd1366d3db38d8";
        #         s:20:"latest_manifest_size";s:7:"6154107";
        #     }
        #     s:7:"version";:8:"4.10.1.0";
        # }
        #
        # a:2 = array of 2 items
        # i:0 ???
        # :8 probably means 8 elements
        #
        # s:7:"version";s:6:"4.10.1";
        # which means:
        # type: string
        # length: 7
        # value: "version"
        return data


class PatcherRequest(BaseRequest):
    def __init__(self, version, os, arch, cookie):
        self.version = version
        self.os = os
        self.arch = arch
        self.cookie = cookie


class PatcherResponse(BaseResponse):
    def __init__(self, response):
        self.response = response

    def ok(self):
        # bad way of checking if a response is ok
        return 'a:1:{s:7:"version";N;}' not in self.deserialize(
            self.response.text
        )


class HonClient:
    def __init__(self, base_url, os, arch, version):
        self.base_url = base_url
        self.os = os
        self.arch = arch
        self.version = version

        user_agent = 'S2 Games/Heroes of Newerth/{version}/{os}/{arch}'.format(
            os=os,
            arch=arch,
            version=SemverUtil(version).four(),
        )

        self.headers = {
            'User-Agent': user_agent,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate',
        }

    def patcher(self, version, cookie):
        endpoint = '/patcher/patcher.php'

        request_data = PatcherRequest(
            os=self.os,
            arch=self.arch,
            version=version,
            cookie=cookie,
        )

        serialized_data = request_data.serialize()

        self.headers['Content-Length'] = '{l}'.format(l=len(serialized_data))
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'

        response = requests.post(
            urljoin(self.base_url, endpoint),
            headers=self.headers,
            data=request_data.serialize()
        )
        response_data = PatcherResponse(response)

        return response_data

    def get_manifest(self, base_url, version, filename):
        endpoint = '/{os}/{arch}/{version}/{filename}'.format(
            os=self.os,
            arch=self.arch,
            version=version,
            filename=filename,
        )

        response = requests.get(
            urljoin(base_url, endpoint),
            headers=self.headers
        )

        if not response.ok:
            raise Exception('Unable to find {endpoint}'.format(
                endpoint=endpoint
            ))

        return ManifestParser(os=self.os, arch=self.arch).extract(
            response=response,
            manifest_filename=filename,
            version=version,
        )

    def get_file(self, path, os, arch, version):
        endpoint = '{os}/{arch}/{version}/{path}'.format(
            os=os,
            arch=arch,
            version=SemverUtil(version).pretty(),
            path=path,
        )

        response = requests.get(
            urljoin(self.base_url, endpoint),
            headers=self.headers
        )

        if not response.ok:
            raise FileNotFoundError(
                'Cannot fetch: ({version}/{client_version}) - {file}'.format(
                    file=path,
                    client_version=version,
                    version=self.version,
                )
            )

        return response
