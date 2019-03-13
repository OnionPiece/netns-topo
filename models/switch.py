import base
import utils

class Switch(base.Base):
    def __init__(self, name, data, collectors):
        super(Switch, self).__init__(name, data, collectors)
        self.interfaces = []

    @utils.single_run()
    def create(self):
        return 'brctl addbr %s' % self.name

    @utils.single_run()
    def up(self):
        return 'ip l set %s up' % self.name

    @utils.single_run(ignore_err=[1])
    def down(self):
        return 'ip l set %s down' % self.name

    @utils.single_run(ignore_err=[1])
    def delete(self):
	return 'brctl delbr %s' % self.name

    @utils.single_run()
    def attach(self, intf):
        return 'brctl addif %s %s' % (self.name, intf)

    @utils.single_run()
    def enable(self, intf):
        return 'ip l set %s up' % intf

    @utils.single_run(ignore_err=[1])
    def detach(self, intf):
        return 'brctl delif %s %s' % (self.name, intf)

    def add_interface(self, intf):
        self.interfaces.append(intf)

    def del_interface(self, intf):
        self.interfaces.remove(intf)

    def setup(self):
        self.create()
        self.up()

    def postSetup(self):
        try:
            for intf in self.interfaces:
                self.attach(intf)
                self.enable(intf)
        except Exception as e:
            raise Exception(
                "Switch %s failed at postSetup, since: %s" % (
                    self.name, e.message))

    def preDestroy(self):
        for intf in self.interfaces:
            self.detach(intf)

    def destroy(self):
        if self.name == '':
            return
        self.down()
        self.delete()
