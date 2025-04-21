#!/bin/bash

ROUTERS=("r1" "r2" "r3" "r4")

for ROUTER in "${ROUTERS[@]}"; do
  
  # install FRR
  docker exec -it $ROUTER apt update
  docker exec -it $ROUTER apt -y install curl gnupg
  docker exec -it $ROUTER bash -c 'curl -s https://deb.frrouting.org/frr/keys.gpg | tee /usr/share/keyrings/frrouting.gpg > /dev/null'
  docker exec -it $ROUTER apt -y install lsb-release
  docker exec -it $ROUTER bash -c 'FRRVER="frr-stable" && echo deb [signed-by=/usr/share/keyrings/frrouting.gpg] https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER | tee -a /etc/apt/sources.list.d/frr.list'
  docker exec -it $ROUTER apt update && docker exec -it $ROUTER apt -y install frr frr-pythontools
  
  # enable daemon
  docker exec -it $ROUTER sed -i 's/ospfd=no/ospfd=yes/g' /etc/frr/daemons
  
  # restart frr
  docker exec -it $ROUTER service frr restart
  
done
