#!/bin/bash

echo "==== Curl manager.abc.com via 10.0.0.3 ===="
echo "==== IP 10.0.0.6 should not been seen as remote addr ===="
echo ""
ip netns exec client sh -c "for i in {1..10} ; do curl -sS manager.abc.com --resolv manager.abc.com:80:10.0.0.3; done"
echo ""
echo "==== Curl monitor.abc.com via 10.0.0.3 ===="
echo "==== Request send to 10.0.0.6 will cause 503 error ===="
echo ""
ip netns exec client sh -c "for i in {1..10} ; do curl -sS monitor.abc.com --resolv monitor.abc.com:80:10.0.0.3; done"
