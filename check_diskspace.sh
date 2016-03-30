#!/bin/sh

df | grep / | while read -r line; do
  partition="$(echo $line | awk '{ print $1 }')"
  usep="$(echo $line | awk '{ print $5 }' | cut -d'%' -f1)"
  if [ $usep -ge 85 ]; then
    echo "Running out of space \"$partition ($usep%)\" on $(hostname) as on $(date)" | mail -s "Alert: Almost out of disk space $usep%" dmheggo
  fi
done

