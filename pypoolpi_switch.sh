#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Not running as root. Relaunching with sudo..."
  exec sudo "$0" "$@"
fi

script_path=$(realpath "$0")
dir_path=$(dirname "$script_path")
parent_path=$(dirname "$dir_path")

systemctl stop pypoolpi.service
rm "$parent_path/pypoolpi"

ln -s "$dir_path" "$parent_path/pypoolpi"
systemctl start pypoolpi.service
