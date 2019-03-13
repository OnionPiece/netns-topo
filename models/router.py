import node
import utils

class Router(node.Node):
    @utils.single_run()
    def disable_rp_filter(self):
        return ('ip netns exec %s sysctl '
                'net.ipv4.conf.all.rp_filter=0' % self.name)

    def setup(self):
        super(Router, self).setup()
        self.enable_forwarding('all')
        self.disable_rp_filter()
