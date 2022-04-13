import ntpath


class SemverException(Exception):
    pass


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

    def next(self, exists=True):
        sv = Semver(self.__str__())

        if exists:
            if sv.hotfix is not None:
                # for 4 digit semvers that exist, the next hotfix version
                sv.hotfix += 1

            if sv.hotfix is None:
                # for 3 digit semvers that exist, the first hotfix version
                sv.hotfix = 0

        else:
            if sv.hotfix is None:
                if sv.minor == 0 and sv.patch == 0:
                    # we ran out of versions
                    raise SemverException('There is no next version')
                elif sv.patch == 0:
                    # for zero 3rd digit semvers, we probably ran out of minor
                    # versions increment major
                    sv.major += 1
                    sv.minor = 0
                    sv.patch = 0
                else:
                    # for non-zero 3rd digit semvers, increment 2nd digit,
                    # set 3rd to 0
                    sv.minor += 1
                    sv.patch = 0

            if sv.hotfix is not None:
                # for 4 digit semvers that don't exist, remove 4th digit
                # increment 3rd by 1
                sv.hotfix = None
                sv.patch += 1

        return sv


class FileUtil:
    def path_leaf(path):  # noqa
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def save_file(filepath, data):  # noqa
        with open(filepath, 'wb') as f:
            f.write(data)

        return filepath
