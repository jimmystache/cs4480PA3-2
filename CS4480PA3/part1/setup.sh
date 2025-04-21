#!/bin/bash


sudo docker compose up -d
sleep 5


./install-frr.sh
sleep 5


./configure-ospf.sh
sleep 10


./configure-host.sh
sleep 2

