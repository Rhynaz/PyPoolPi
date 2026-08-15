#!/bin/bash

script_path=$(realpath "$0")
dir_path=$(dirname "$script_path")

uid=$(stat -c "%u" "$dir_path")

cd "$dir_path"
exec setpriv --reuid=$uid --regid=$uid --init-groups python3.13 main.py "$@"
