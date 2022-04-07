import ntpath


class SemverUtil:
    def create(major, minor, patch, hotfix=None):
        version = f'{major}.{minor}.{patch}'

        if hotfix is not None:
            version = f'{version}.{hotfix}'

        return version


# Semver
class Semver:
    def __init__(self, semver):
        self.items = semver.split('.')

        # digits
        self.major = int(self.items[0])
        self.minor = int(self.items[1])
        self.patch = int(self.items[2])
        self.hotfix = int(self.items[3]) if len(self.items) == 4 else None

    def __str__(self):
        return SemverUtil.create(
            self.major, self.minor, self.patch, self.hotfix
        )

    # 1.2.3
    def three(self):
        return SemverUtil.create(
            self.major, self.minor, self.patch
        )

    # 1.2.3.0
    def four(self):
        return SemverUtil.create(
            self.major, self.minor, self.patch, self.hotfix or 0
        )

    # Pretty print semver. This ensures that a fourth digit is only displayed
    # if it is something other than 0.
    #
    # - 3.1.0 becomes 3.1.0
    # - 3.1.0.0 becomes 3.1.0
    # - 3.1.0.1 becomes 3.1.0.1
    def pretty(self):
        # ignore trailing '0' on 4 digit semvers
        hotfix = None if self.hotfix == 0 else self.hotfix

        return SemverUtil.create(
            self.major, self.minor, self.patch, hotfix
        )



class FileUtil:
    def path_leaf(path):  # noqa
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def save_file(filepath, data):  # noqa
        with open(filepath, 'wb') as f:
            f.write(data)

        return filepath
