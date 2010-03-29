from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

class Config(SafeConfigParser):
    def __init__(self, file):
        SafeConfigParser.__init__(self)
        self.read(file)

    def getstring(self, item, default=""):
        section, option = item.split('.')
        try:
            val = self.get(section, option, 1)
        except (NoSectionError, NoOptionError):
            val = default
        return val

    def getbool(self, item, default=False):
        section, option = item.split('.')
        try:
            val = self.getboolean(section, option)
        except (NoSectionError, NoOptionError):
            val = default
        return val
