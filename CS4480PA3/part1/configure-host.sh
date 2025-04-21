#!/bin/bash

# routes on ha
docker exec -it ha ip route del default
# add a route to r1
docker exec -it ha ip route add default via 10.0.14.4

# routes on hb
docker exec -it hb ip route del default
# add a route to r3
docker exec -it hb ip route add default via 10.0.15.4

