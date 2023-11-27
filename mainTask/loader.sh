#!/bin/bash

root_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if  [ ! -f "$root_dir/mosquitto/certs/CA/ca_crt.der" ]; then 
    echo "$root_dir/mosquitto/certs/CA/ca_crt.der not found"
    exit
fi
if [ ! -f "$root_dir/mosquitto/certs/clients/$1/${1}_crt.der" ]; then 
    echo "$root_dir/mosquitto/certs/clients/$1/${1}_crt.der not found"
    exit
fi
if [ ! -f "$root_dir/mosquitto/certs/clients/$1/${1}_key.der" ]; then
    echo "$root_dir/mosquitto/certs/clients/$1/${1}_key.der not found"
    exit
fi

if [ ! -d "$root_dir/micropython_data/certs" ]; then
    mkdir $root_dir/micropython_data/certs
else
    rm $root_dir/micropython_data/certs/*
fi

cp $root_dir/mosquitto/certs/clients/$1/${1}_crt.der $root_dir/micropython_data/certs/esp_crt.der
cp $root_dir/mosquitto/certs/clients/$1/${1}_key.der $root_dir/micropython_data/certs/esp_key.der
cp $root_dir/mosquitto/certs/CA/ca_crt.der $root_dir/micropython_data/certs/ca_crt.der

#Connection
python3 -m mpremote soft-reset + run $root_dir/reset.py
python3 -m mpremote mkdir ./certs
python3 -m mpremote cp $root_dir/micropython_data/certs/esp_crt.der :certs/
python3 -m mpremote cp $root_dir/micropython_data/certs/esp_key.der :certs/
python3 -m mpremote cp $root_dir/micropython_data/certs/ca_crt.der :certs/

python3 -m mpremote cp $root_dir/micropython_data/boot.py :
python3 -m mpremote cp $root_dir/micropython_data/main.py :
python3 -m mpremote cp $root_dir/micropython_data/wifi.conf :

python3 -m mpremote ls