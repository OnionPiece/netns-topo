import base
import utils

class Modprobe(base.Base):
    def __init__(self, name, data, collectors):
        super(Modprobe, self).__init__(name, data, collectors)

    @utils.single_run()
    def setup(self):
        return 'modprobe %s' % (' '.join(self.data))

    @utils.single_run()
    def destroy(self):
        return 'modprobe -r %s' % (' '.join(self.data))
