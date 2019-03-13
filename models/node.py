import base
import confs
import json
import utils

class Node(base.Base):
    def __init__(self, name, data, collectors):
        super(Node, self).__init__(name, data, collectors)

    def get_switch_interface_name(self, switch_name):
        return '%s-%s' % (switch_name, self.name)

    def get_ns_interface_name(self, switch_name):
        return '%s-%s' % (self.name, switch_name)

    def validate_and_set_data(self, data):
        if 'interfaces' not in data:
            raise Exception("Node/router miss attr interfaces")
        self.interfaces = data['interfaces']
        self.default_route = data.get('default_route', '')
        self.extra_routes = data.get('extra_routes', {})
        self.services = data.get('service', [])
        self.endpoints = {}

        for switch_name in self.interfaces.iterkeys():
            switch_intf = self.get_switch_interface_name(switch_name)
            trans_len = len(switch_intf)
            if trans_len > 15:
                raise Exception(
                    "Node/router %s interface name on switch %s is too long "
                    "after trans, len(%s) > 15" % (
                        self.name, switch_name, switch_intf))

    @utils.single_run()
    def create(self):
        return 'ip netns add %s' % self.name

    @utils.single_run(ignore_err=[1])
    def delete(self):
	return 'ip netns del %s' % self.name

    @utils.single_run()
    def set_interface_up(self, dev):
        return 'ip netns exec %s ip l set %s up' % (self.name, dev)

    @utils.single_run()
    def set_interface_cidr(self, dev, cidr):
        return 'ip netns exec %s ip a add dev %s %s' % (self.name, dev, cidr)

    @utils.single_run()
    def create_and_attach_interface(self, switch_intf, ns_intf):
        return 'ip l add %s type veth peer name %s netns %s' % (
            switch_intf, ns_intf, self.name)

    @utils.single_run()
    def attach_interface(self, dev):
        return 'ip l set %s up netns %s' % (dev, self.name)

    @utils.single_run()
    def detach_interface(self, ns_intf):
        return 'ip netns exec %s ip l del %s' % (self.name, ns_intf)

    @utils.single_run()
    def add_route(self, dst, nh):
        if 'onlink' in nh:
            nh, dev, _ = nh.split()
            return 'ip netns exec %s ip r add %s via %s dev %s onlink' % (
                self.name, dst, nh, dev)
        elif 'devonly' in nh:
            dev, _ = nh.split()
            return 'ip netns exec %s ip r add %s dev %s' % (
                self.name, dst, dev)
        else:
            return 'ip netns exec %s ip r add %s via %s' % (self.name, dst, nh)

    @utils.single_run()
    def enable_proxy_arp(self, dev):
        return ('ip netns exec %s sysctl '
                'net.ipv4.conf.%s.proxy_arp=1' % (self.name, dev))

    @utils.single_run()
    def enable_forwarding(self, dev):
        return ('ip netns exec %s sysctl '
                'net.ipv4.conf.%s.forwarding=1' % (self.name, dev))

    @utils.single_run()
    def run_service(self, svc, args=None):
        try:
            params = {'confs': confs.abspath, 'node': self.name}
            if args:
                params.update(json.loads(args))
            cmd = 'ip netns exec %s %s' % (self.name, svc % params)
        except Exception as e:
            raise Exception(
                "Failed to parse service %s for node/router %s, since: %s" % (
                    svc, self.name, e.message))
        return cmd

    def add_endpoint(self, dev_name, cidr):
        self.endpoints[dev_name] = cidr

    def set_interfaces(self):
        for switch_name, cidrs in self.interfaces.iteritems():
            switch_intf = self.get_switch_interface_name(switch_name)
            ns_intf = self.get_ns_interface_name(switch_name)
            self.create_and_attach_interface(switch_intf, ns_intf)
            self.set_interface_up(ns_intf)
            for cidr in cidrs.split(',') if ',' in cidrs else cidrs.split():
                self.set_interface_cidr(ns_intf, cidr)
            self.collectors[switch_name].add_interface(switch_intf)

    def setup(self):
        self.create()
        self.set_interfaces()
        if self.default_route:
            self.add_route('default', self.default_route)
        for dst, nh in self.extra_routes.iteritems():
            if 'onlink' in nh:
                _, dev, _ = nh.split()
                self.set_interface_up(dev)
            self.add_route(dst, nh)

    def setup_endpoints(self):
        with_eps = False
        for ep_dev, cidr in self.endpoints.iteritems():
            self.attach_interface(ep_dev)
            self.enable_forwarding(ep_dev)
            self.enable_proxy_arp(ep_dev)
            self.add_route(cidr, '%s devonly' % ep_dev)
            with_eps = True
        if with_eps:
            self.set_interface_up('lo')
            self.add_route('169.254.1.1', 'lo devonly')

    def setup_services(self):
        for svc in self.services:
            if ' ' in svc:
                svc, args = svc.split(' ', 1)
            else:
                args = None
            self.run_service(
                self.collectors['services'].get_service(svc), args)

    def postSetup(self):
        try:
            self.setup_endpoints()
            self.setup_services()
        except Exception as e:
            raise Exception(
                "Node/Router %s failed at postSetup, since: %s" % (
                    self.name, e.message))

    def clean_services(self):
        for svc in self.services:
            cleanSvc = self.collectors['services'].get_service(svc + "_clean")
            if not cleanSvc:
                continue
            self.run_service(cleanSvc)

    def clean_interfaces(self):
        for switch_name in self.interfaces.iterkeys():
            ns_intf = self.get_ns_interface_name(switch_name)
            self.detach_interface(ns_intf)

    def preDestroy(self):
        if not utils.ns_exists(self.name):
            return
        self.clean_services()
        self.clean_interfaces()

    def destroy(self):
        self.delete()
