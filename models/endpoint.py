import confs
import node
import utils

class Endpoint(node.Node):
    def __init__(self, name, data, collectors):
        super(Endpoint, self).__init__(name, data, collectors)

    def validate_and_set_data(self, data):
        if 'veth' not in data:
            raise Exception("Endpoint miss attr veth")
        self.peer = data['veth'].keys()[0]
        self.cidr = data['veth'][self.peer]
        self.peer_dev = '%s-%s' % (self.peer, self.name)
        self.dev = '%s-%s' % (self.name, self.peer)
        trans_len = len(self.dev)
        if trans_len > 15:
            raise Exception(
                "Endpoint %s veth name in target %s is too long "
                "after trans, len(%s) > 15" % (
                    self.name, self.peer, self.dev))
        self.default_route = "169.254.1.1 %s onlink" % self.dev
        self.services = data.get('service', [])

    def set_interfaces(self):
        self.create_and_attach_interface(self.peer_dev, self.dev)
        self.set_interface_up(self.dev)
        self.set_interface_cidr(self.dev, self.cidr)
        self.collectors[self.peer].add_endpoint(self.peer_dev, self.cidr)

    def setup(self):
        self.create()
        self.set_interfaces()
        self.add_route('default', self.default_route)

    def postSetup(self):
        try:
            self.setup_services()
        except Exception as e:
            raise Exception(
                "Endpoint %s failed at postSetup, since: %s" % (
                    self.name, e.message))

    def clean_interfaces(self):
        self.detach_interface(self.dev)
