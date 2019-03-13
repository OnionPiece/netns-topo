#!/bin/bash
#
# use nc to test UDP
# server: sh -c "echo test | nc -l -u -p 53"
# client: sh -c "nc -vzu 10.128.9.80 53"
#     10.128.9.80 (10.128.9.80:53) open   => success
#     None                                => fail
# need restart server when restart client
# 
# TCP: 53, 80, 443, 1936, 8080
# UDP: 53, 111, 123, 2049, 20048, 20049, 20050

in_netns=1
cmd_prefix=""
if [[ $in_netns -eq 1 ]]; then
    cmd_prefix="ip netns exec server"
fi
first_udp_port=53
last_udp_port=20050
ALL_UDP_PORTS=($first_udp_port 111 123 2049 20048 20049 $last_udp_port)
first_tcp_port=53
last_tcp_port=30000
ALL_TCP_PORTS=($first_tcp_port 80 443 1936 8080 8443 9100 9125 10250 $last_tcp_port)

port=${1:-$first_udp_port}
proto=${2:-udp}

echo "listen for $proto port $port"
if [[ $proto == "udp" ]]; then
    $cmd_prefix sh -c "echo -e 'Remote $proto port $port \tis reachable' | nc -l -u -p $port" &
    if [[ $port == $last_udp_port ]]; then
        exit
    fi
    next_port=""
    for i in "${!ALL_UDP_PORTS[@]}"; do
       if [[ "${ALL_UDP_PORTS[$i]}" = "${port}" ]]; then
           next_port=${ALL_UDP_PORTS[$((i+1))]}
       fi
    done
    bash ./$0 $next_port
    
    if [[ $port != $first_udp_port ]]; then
        exit
    fi

    bash ./$0 $first_tcp_port tcp
else
    $cmd_prefix sh -c "echo -e 'Remote $proto port $port \tis reachable' | nc -l -p $port" &
    if [[ $port == $last_tcp_port ]]; then
        exit
    fi
    next_port=""
    for i in "${!ALL_TCP_PORTS[@]}"; do
       if [[ "${ALL_TCP_PORTS[$i]}" = "${port}" ]]; then
           next_port=${ALL_TCP_PORTS[$((i+1))]}
       fi
    done
    bash ./$0 $next_port tcp
    exit
fi

echo "Will wait for 10 seconds..."
for i in {10..1}; do 
    echo "${i}..."
    sleep 1
done
if [[ $in_netns -eq 1 ]]; then
    ip netns pids server | xargs kill -9 &
else
    pkill -9 -f "nc -l" &
fi
