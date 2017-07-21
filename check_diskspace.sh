#!/bin/sh

df -h | grep / | while read -r line; do
  partition="$(echo $line | awk '{ print $1 }')"
  avail="$(echo $line | awk '{ print $4 }')"
  usep="$(echo $line | awk '{ print $5 }' | cut -d'%' -f1)"
  if [ $usep -ge 92 ]; then
    printf "Host: %s\nPartition: %s\nSpace left: %s" "$(hostname)" "$partition" "$avail" | mail -s "Alert: Partition on $(hostname) is $usep% full" dmheggo
  fi
done
