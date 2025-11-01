#!/bin/bash

# =========================================================
# Lunit VM GPU Status Checker
# =========================================================
# This script connects to each of the 14 working VMs and runs 'nvidia-smi'.
# It uses a 10-second timeout for each connection attempt.

# List of IPs for the VMs that were successfully set up.
# Excluded the two problematic IPs: 61.107.202.169 and 61.107.202.194
SUCCESSFUL_IPS=(
    "61.107.202.89"
    "61.107.202.163"
    "61.107.202.164"
    "61.107.202.166"
    "61.107.202.167"
    "61.107.202.168"
    # IP for vm22 (61.107.202.169) is excluded
    "61.107.202.171"
    "61.107.202.172"
    "61.107.202.173"
    "61.107.202.174"
    "61.107.202.175"
    "61.107.202.176"
    "61.107.202.177"
    "61.107.202.178"
)

echo "========================================================"
echo "Starting GPU Status Check on 14 Lunit VMs..."
echo "========================================================"

# Loop through each IP address and check the GPU status
for IP in "${SUCCESSFUL_IPS[@]}"; do
    echo ""
    echo "############################################################"
    echo "### Checking GPU Status on: lunit@$IP ###"
    echo "############################################################"
    
    # Connect via SSH with a 10-second timeout and execute nvidia-smi
    ssh -o ConnectTimeout=10 lunit@$IP "nvidia-smi"
done

echo ""
echo "========================================================"
echo "GPU status check complete for all 14 reachable VMs."
echo "========================================================"
