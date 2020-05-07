---
layout: post
title: "Linux Shell Script"
date: 2020-04-22 12:00
categories: Linux
tags: Linux, Shell, Shell Script
---

```c
#!/bin/bash

CPU_CLI_1=$(lscpu | egrep 'Core|Socket|Model name')
CPU_CLI_2=$(dmidecode -t processor | egrep 'Upgrade' | tail -1 | awk '{print $2}')
CPU_CLI_3=$(dmidecode -t processor | egrep 'Upgrade' | tail -1 | cut -d ":" -f 2)
CPU_CLI_4="lshw"

MEM_CLI_1=$(dmidecode -t 17 | egrep 'Memory|Size|Type:|Part Number' | sed -n '1,4p')
MEM_CLI_2=$(dmidecode -t 17 | egrep 'Memory Device' | wc -l)
MEM_CLI_3=$(free -mh | egrep 'Mem' | awk '{print $2}')

DISK_CLI=$(lsblk | egrep 'disk')

lshw_cmd() {
    lshw -C CPU | egrep 'slot' | awk '{print $2}'
}

echo "====== CPU_INFO ======"
echo "$CPU_CLI_1"

CPU_CLI_2_RESULT=$CPU_CLI_2

if [ $CPU_CLI_2_RESULT == "Other" ];
then
    { `$CPU_CLI_4 > /dev/null 2>&1` &&
        result="$(lshw_cmd)"
        echo -e "SocketType:\t       $result"
    } || {
        echo "SocketType: Other"
    }
else
    echo -e "SocketType:\t       $CPU_CLI_3"
fi

echo "====== MEM_INFO ======"
echo "$MEM_CLI_1"
echo "SLOTS: $MEM_CLI_2"
echo "TOTAL MEM: $MEM_CLI_3"


echo "====== DISK_INFO ======"
echo "$DISK_CLI"

```
