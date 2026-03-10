#!/bin/bash

while true
do
    echo "----- NODE INFO -----"
    hostname

    echo "Active iSCSI sessions:"
    iscsiadm -m session || true

    echo "Targets configured:"
    targetcli ls /iscsi || true

    sleep 60
done