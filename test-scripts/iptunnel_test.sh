#!/bin/bash

echo "Curl each endpoints from endpoints, only endpoint IP should be seen in remote addr"
echo ""
for i in 10.0.1.101 10.0.1.102 10.0.1.103 10.0.2.101 10.0.2.102 10.0.2.103; do
    for j in endpoint1 endpoint2 endpoint3 endpoint4 endpoint5 endpoint6 ; do
        ip netns exec $j ip a | grep -q $i
        if [[ $? -eq 0 ]]; then
            continue
        fi
        ip netns exec $j curl $i --connect-timeout 1
        if [[ $? -ne 0 ]]; then
            echo "Failed curl from $j to $i"
        fi
    done
done

echo ""
echo "Curl node3 from endpoints, endpoint1, endpoint3, endpoint4 should seen VIP in remote addr"
echo "other endpoints should failed"
echo ""
for i in endpoint1 endpoint2 endpoint3 endpoint4 endpoint5 endpoint6 ; do
    ip netns exec $i curl 10.0.0.13 --connect-timeout 1
done
