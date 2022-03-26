import ntpath


# Semver util
class SemverUtil:
    def __init__(self, _semver):
        self._semver = _semver
        self.items = _semver.split('.')

    def _create_semver(self, items):
        return '.'.join(items)

    # 1.2.3
    def three(self):
        return self._create_semver(self.items[:3])

    # 1.2.3.0
    def four(self):
        _items = self.items

        if len(_items) < 4:
            _items.append('0')

        return self._create_semver(_items)

    # Pretty print semver. This ensures that a fourth digit is only displayed
    # if it is something other than 0.
    #
    # - 3.1.0 becomes 3.1.0
    # - 3.1.0.0 becomes 3.1.0
    # - 3.1.0.1 becomes 3.1.0.1
    def pretty(self):
        # ignore trailing '0' on 4 digit semvers
        if len(self.items) > 3 and self.items[-1] == '0':
            return self._create_semver(self.items[:-1])

        return self._create_semver(self.items)


class FileUtil:
    def path_leaf(path):  # noqa
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def save_file(filepath, data):  # noqa
        with open(filepath, 'wb') as f:
            f.write(data)

        return filepath
