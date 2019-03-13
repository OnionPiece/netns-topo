# netns-topo
A simple script tool to deploy L2-L3 networking environment with netns,
linuxbridge on a single VM/laptop, for networking tests.

## Commands
Need run under netns-topo directory.

    # To setup a topology based on given yaml.
    ./run.py -s /path/to/topology/yaml
    # To destroy current topology.
    ./run.py -d

Only one topology could be setup each time.

## Directories
- topologies --- where topology yamls are placed;
- confs --- where service configure files are placed, service like haproxy, keepalived which will be running in namespace;
- test-scripts --- where test scripts are placed.
- deprecated --- previous version run.py is placed here.

## Topology yaml
### model
#### description
Descriptions will be printed after topology setup.

    description: |
        ...things will be printed...

#### services
Services list will be running in namespaces.

    services:
        SERVICE_NAME: COMMAND
        SERVICE_NAME_clean: how to stop/cleanup service

A service referred by a namespace will run like "ip netns exec NS_NAME COMMAND", so you don't need to specify "ip netns exec NS_NAME" in service command part.

For complex command, you may need sh -c "...".

Service command accepts variables in Python string format style, like "%(args)s". And later in where service is referred, parameters(variable map) should be passed just after service, no blank is allowed in variable map, e.g. :

    services:
        myService1: SOME-COMMANDS --port %(listen_port)s --log-level %(log-level)s

    (...where it is referred...)
        service:
            - myService1 {"listen_port":"1025","log-level":"2"}
            - myService1 {"listen_port":"1026","log-level":"2"}

Two builtin variable for common service command:
  - %(confs)s: will be replaced by confs directory absolute path.
  - %(node)s: will be replaced by namespace name.

Builtin services, check models/services.py for more details, each builtin service may have its specified variables:
  - setupTunl0
  - snat
  - skipSnat
  - snatDest
  - echoService

#### modprobe
Will run "modprobe MOD ..." for setup and "modprobe -r MOD ..." for destroy.

    modprobe:
        - MOD_1
        - MOD_2

#### switch

    SWITCH_NAME:
        type: switch

#### node

    NODE_NAME:
        type: node
        interfaces:
            SWITCH_NAME1: IP1 IP2 ...
            SWITCH_NAME2: IPn
        extra_routes:
            DESTINATION1: NEXTHOP1
            DESTINATION2: DEV devonly
            DESTINATION3: NEXTHOP3 DEV onlink
            ...
        default_route: GATEWAY_IP
        service:
            - SERVICE_NAME1
            - SERVICE_NAME2
            - ...

An interface can have multiple IP addresses, each IP should be seperated by comma or blank.

extra_routes, default_route, service are optional attributes.

For extra_routes, devonly and onlink are keywards, for add route with DEV parameter only, and add route with onlink.

No need to putting SERVICE_NAME_clean in service, they will be automatically called when destroy.

For service need parameters, check above services section.
 
#### router
Router is similar to node, but with type is router.

Currently, the only difference between node and router is, forwarding will be enabled in router and rp_filter will be disabled in router.

## Requirements
  - PyYAML
  - python-netaddr
  - bridge-utils
  - gunicorn and flask (optional)
  - keepalived (optional)
  - haproxy(optional)

## Known issue
Sometime restarting network service is needed, or virtual network topology
won't work, virtual node is not reachable for each other.
