#!/bin/bash


for router in r1 r2 r3 r4; do
  docker exec -it $router service frr restart
done

# wait for FRR 
sleep 5
./r1-ospf.sh
./r2-ospf.sh
./r3-ospf.sh
./r4-ospf.sh

# wait for OSPF
# sleep 10

# for router in r1 r2 r3 r4; do
#   docker exec -it $router vtysh -c 'show ip ospf neighbor'
# done

# for router in r1 r2 r3 r4; do
#   docker exec -it $router vtysh -c 'show ip route'
# done
