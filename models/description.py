import base

class Description(base.Base):
    def __init__(self, name, data, collectors):
        super(Description, self).__init__(name, data, collectors)
