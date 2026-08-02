#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Not running as root. Relaunching with sudo..."
  exec sudo "$0" "$@"
fi

echo "--- Installing Dependencies ---"
apt -y install python3-gpiozero

apt -y install python3-flask python3-waitress
apt -y install python3-paho-mqtt

apt -y install python3-mashumaro
apt -y install python3-tomli python3-tomli-w

apt -y install python3-watchdog

echo "--- Setting Network Capabilities ---"
setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/python3.13

echo "--- Installing PyPoolPi ---"
script_path=$(realpath "$0")
dir_path=$(dirname "$script_path")
parent_path=$(dirname "$dir_path")

ln -sf "$dir_path" "$parent_path/pypoolpi"
echo "Created symlink '$dir_path' → '$parent_path/pypoolpi'."

ln -sf "$parent_path/pypoolpi/pypoolpi.sh" "/usr/local/bin/pypoolpi"
echo "Created symlink '$parent_path/pypoolpi/pypoolpi.sh' → '/usr/local/bin/pypoolpi'."

systemctl enable --now "$parent_path/pypoolpi/pypoolpi.service"
