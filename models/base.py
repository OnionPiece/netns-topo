class Base(object):
    def __init__(self, name, data, collectors, prefix=''):
        self.prefix = prefix
        self.validate_and_set_name(name)
        self.validate_and_set_data(data)
        self.collectors = collectors
        self.collectors[name] = self
        self.data = data

    def validate_and_set_name(self, name):
        trans_len = len(self.prefix + name)
        if trans_len > 15:
            raise Exception(
                "%s name is too long after trans, len(%s) > 15" % (
                    name, trans_len))
        self.name = self.prefix + name

    def validate_and_set_data(self, data):
        pass

    def preSetup(self):
        pass

    def setup(self):
        pass

    def postSetup(self):
        pass

    def preDestroy(self):
        pass

    def destroy(self):
        pass

    def postDestroy(self):
        pass

    def echo_data(self):
        print self.data
