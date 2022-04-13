import requests
from tokenize import tokenize, NUMBER, STRING, OP, NAME
from io import BytesIO

from urllib.parse import urljoin

from manifest import ManifestParser
from utils import Semver


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
        self.tokens = self.tokenize()

    def tokenize(self):
        # parse patcher data
        patcher_tokens = tokenize(
            BytesIO(self.response.content).readline
        )

        # convert tokens to json
        values = list()
        local_values = list()
        indentation = 0

        for toknum, tokval, _, _, _ in patcher_tokens:
            if toknum == OP:
                if tokval == '}':
                    values.append(
                        dict(zip(
                            # even items
                            local_values[::2],
                            # odd items
                            local_values[1::2]
                        ))
                    )
                    local_values = []

            if toknum == NAME and tokval == 'N':
                # null value
                local_values.append(None)

            if toknum == STRING:
                local_values.append(tokval.strip('"'))

        return values

    def ok(self):
        # bad way of checking if a response is ok
        return self.tokens[-1]['version'] is not None


class HonClient:
    def __init__(self, base_url, os, arch, version):
        self.base_url = base_url
        self.os = os
        self.arch = arch
        self.version = version

        user_agent = 'S2 Games/Heroes of Newerth/{version}/{os}/{arch}'.format(
            os=os,
            arch=arch,
            version=Semver(version).four(),
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
            version=Semver(version).pretty(),
            path=path,
        )

        response = requests.get(
            urljoin(self.base_url, endpoint),
            headers=self.headers
        )

        if not response.ok:
            raise FileNotFoundError('Cannot fetch: {file}'.format(file=path))

        return response
