import description
import endpoint
import modprobe
import node
import os
import router
import services
import switch
import utils


TOP = True
BOTTOM = False
DEFAULT_MTU = 1500
LOCK = '/var/lib/netns-topo.lock'


def unsupport_type(item, data, *args):
    raise Exception(
        'Unsupported item %s or its type is unsupport' % (item))

model_map = {
    'switch': switch.Switch,
    'description': description.Description,
    'modprobe': modprobe.Modprobe,
    'services': services.Services,
    'node': node.Node,
    'router': router.Router,
    'endpoint': endpoint.Endpoint,
}

def setup(topo_yaml, topo_d):
    collectors = {}
    try:
        for item, data in topo_d.iteritems():
            model = model_map.get(item, False) or model_map.get(
                data['type'] if isinstance(data, dict) else 'unknown',
                unsupport_type)
            model(item, data, collectors)
        for obj in collectors.itervalues():
            obj.preSetup()
        for obj in collectors.itervalues():
            obj.setup()
        for obj in collectors.itervalues():
            obj.postSetup()
    except Exception as e:
        print "Exception happend during setup, start cleanup"
        print e.message
        for obj in collectors.itervalues():
            obj.preDestroy()
        for obj in collectors.itervalues():
            obj.destroy()
        for obj in collectors.itervalues():
            obj.postDestroy()
    else:
        with open(LOCK, 'w+') as f:
            f.write(topo_yaml)
        obj = collectors.get('description')
        if obj:
            obj.echo_data()

def destroy(topo_d):
    collectors = {}
    try:
        for item, data in topo_d.iteritems():
            model = model_map.get(item, False) or model_map.get(
                data['type'] if isinstance(data, dict) else 'unknown',
                unsupport_type)
            model(item, data, collectors)
        for obj in collectors.itervalues():
            obj.preDestroy()
        for obj in collectors.itervalues():
            obj.destroy()
        for obj in collectors.itervalues():
            obj.postDestroy()
    except Exception as e:
        print e.message
    else:
        os.remove(LOCK)

def setup_or_destroy(topo_yaml, method):
    topo_d = utils.get_topo(topo_yaml)
    if not topo_d:
        print "No invalid yaml topo found."
        return

    if method == "setup":
        setup(topo_yaml, topo_d)
    else:
        destroy(topo_d)
