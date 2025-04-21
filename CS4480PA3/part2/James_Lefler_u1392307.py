#!/usr/bin/env python3

import os
import subprocess
import argparse
import time
import sys

def run_command(command, silent=False):
    """Execute a shell command and optionally print output"""
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, text=True, capture_output=True)
        else:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            
        if not silent and result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False, e.stderr
def create_topology():
    """makes network topology"""
    print("making topology...")
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../part1"))

    run_command("sudo docker compose up -d")
    time.sleep(5)
    print("done!")
    return True

def configure_routers():
    """configure OSPF on all routers"""    
    part1_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../part1")
    os.chdir(part1_dir)

    print("configuring routers...")
    print("installfrr..")
    run_command("./install-frr.sh")
    time.sleep(3)
    print("config ospf...")
    run_command("./configure-ospf.sh")
    time.sleep(3)
    print("done!")
    return True

def configure_host_routes():
    """configure routes for the hosts"""
    part1_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../part1")
    os.chdir(part1_dir)

    print("configuring routes...")
    run_command("./configure-host.sh")
    time.sleep(2)
    print("done!")
    return True

def set_interface_cost(router, interface, cost):
    """set OSPF cost for a specific interface path"""
    cmd = f"sudo docker exec -it {router} vtysh -c 'configure terminal' -c 'interface {interface}' -c 'ip ospf cost {cost}' -c 'exit' -c 'write'"
    success, _ = run_command(cmd)
    return success

def move_traffic_top():
    """configure network to prefer the top path"""
    print("moving path to top...")
    set_interface_cost("r1", "eth0", 10)  # R1-R2 interface
    set_interface_cost("r2", "eth0", 10)  # R2-R1 interface
    set_interface_cost("r2", "eth1", 10)  # R2-R3 interface
    set_interface_cost("r3", "eth0", 10)  # R3-R2 interface
    
    set_interface_cost("r1", "eth1", 20)  # R1-R4 interface
    set_interface_cost("r4", "eth1", 20)  # R4-R1 interface
    set_interface_cost("r4", "eth0", 20)  # R4-R3 interface
    set_interface_cost("r3", "eth1", 20)  # R3-R4 interface
    time.sleep(3)
    print("done!")
    return True

def move_traffic_bottom():
    """configure network to prefer the bottom path"""    
    print("moving path to bottom...")
    set_interface_cost("r1", "eth0", 20)  # R1-R2 interface
    set_interface_cost("r2", "eth0", 20)  # R2-R1 interface
    set_interface_cost("r2", "eth1", 20)  # R2-R3 interface
    set_interface_cost("r3", "eth0", 20)  # R3-R2 interface
    
    set_interface_cost("r1", "eth1", 10)  # R1-R4 interface
    set_interface_cost("r4", "eth1", 10)  # R4-R1 interface
    set_interface_cost("r4", "eth0", 10)  # R4-R3 interface
    set_interface_cost("r3", "eth1", 10)  # R3-R4 interface
    time.sleep(3)
    print("done")
    return True

def get_current_path():
    """checks which path is used"""
    worked, output = run_command("sudo docker exec -it ha traceroute -n 10.0.15.3", silent=True)
    if worked and "10.0.13.3" in output:
        return "bottom"  # R1-R4-R3 path
    else:
        return "top"  # R1-R2-R3 path

def toggle_path():
    """toggle between top and bottom path"""
    current_path = get_current_path()    
    if current_path == "top":
        move_traffic_bottom()
    else:
        move_traffic_top()
    
    return True

def main():
    """main function to parse arguments perform network functions"""
    parser = argparse.ArgumentParser(
        description="Network Orchestrator for managing paths in a router topology",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Define the mutually exclusive group for the main operations
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", action="store_true", 
                       help="Create the network topology")
    group.add_argument("--configure-ospf", action="store_true", 
                       help="Configure OSPF on routers")
    group.add_argument("--host-routes", action="store_true", 
                       help="Configure routes on hosts")
    group.add_argument("--top", action="store_true", 
                       help="Move traffic to the top path (R1-R2-R3)")
    group.add_argument("--bottom", action="store_true", 
                       help="Move traffic to the bottom path (R1-R4-R3)")
    group.add_argument("--toggle", action="store_true", 
                       help="Toggle between top and bottom paths")
    group.add_argument("--setup-all", action="store_true", 
                       help="Run complete setup")
    
    args = parser.parse_args()
    
    # Execute the selected operation
    if args.create:
        create_topology()
    elif args.configure_ospf:
        configure_routers()
    elif args.host_routes:
        configure_host_routes()
    elif args.top:
        move_traffic_top()
    elif args.bottom:
        move_traffic_bottom()
    elif args.toggle:
        toggle_path()
    elif args.setup_all:
        create_topology()
        configure_routers()
        configure_host_routes()
        current_path = get_current_path()
if __name__ == "__main__":
    main()
