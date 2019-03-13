import base

class Services(base.Base):
    def __init__(self, name, data, collectors):
        super(Services, self).__init__(name, data, collectors)
        self.load_builtin_services()

    def get_service(self, service):
        svc = self.data.get(service)
        if not svc and not service.endswith('_clean'):
            raise Exception("service %s not found" % service)
        return svc

    def load_builtin_services(self):
        self.data.update({
            'setupTunl0': 'ip l set tunl0 up mtu 1440',
            'skipSnat': 'iptables -t nat -A POSTROUTING -s %(src)s -d %(dst)s -j ACCEPT',
            'snatDest': 'iptables -t nat -A POSTROUTING -s %(src)s -d %(dst)s -j SNAT --to-source %(to)s',
            'snat': 'iptables -t nat -A POSTROUTING -s %(src)s -j SNAT --to-source %(to)s',
            'echoService': 'gunicorn -b 0.0.0.0:80 flask-svc.flask-echo-svc:application -D -p /var/run/%(node)s_gunicorn.pid',
            'echoService_clean': 'pkill -F /var/run/%(node)s_gunicorn.pid',
        })
