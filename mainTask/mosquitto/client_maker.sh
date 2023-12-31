#!/bin/bash

# you call this script using ./client_maker pem/der username <optional keytype RSA/EC/ED25519>
# eg ./client_maker pem user1 OR ./client_maker der user2
# The script WILL NOT DELETE ANYTHING - it just renames any certs dir that it finds

# You will probably need to change this for your system
mosquitto_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Note: Pico W can use EC or RSA keys only, not EC25519, and Tasmota can only use 2048 bit RSA keys.

# Default choice of Key Types: RSA, EC, or ED25519 (if it hasn't been given as Argument $3)
key_type='EC'

# Choice of NIST Curves for EC Keys: P-256, P-384 or P-521
curve='P-256'

# Choice of Bits for RSA Keys: 2048 or 4096
rsa_bits='2048'

# How many days is the Cert valid for?
days='365'

############################################################
#   End of user defined variables
############################################################

# Sanity check: have you called the script correctly?
[ -z "$1" ] | [ -z "$2" ] && printf "\n Missing aurguments...\n\n  Enter either DEM or PEM then the username \n  eg: client_maker pem user1 \n  or  client_maker der user2\n\n  You can also override the default Key Type by adding RSA, EC, or ED25519 as an optional third argument\n\n  eg: client_maker pem user1 EC\n\n" && exit 1

# If Argument $3 has been given, override the default key_type given above
if [ -n "$3" ]
then
  key_type=$3
fi


# Which output Format Type do we need to use?
if [ $1 = 'PEM' ] || [ $1 = 'pem' ]; then
format_type="pem"
elif [ $1 = 'DER' ] || [ $1 = 'der' ]; then
format_type="der"
fi

# Set the algorithm
algorithm="-algorithm ${key_type}"

# Set the specific pkeyopt for the chosen algorithm (BLANK for ED25519)
if [ "${key_type}" == "EC" ]; then 
  echo 'Create EC Key'
  pkeyopt="-pkeyopt ec_paramgen_curve:${curve}"
elif [ "${key_type}" == "RSA" ]; then
  echo 'Create RSA Key'
  pkeyopt="-pkeyopt rsa_keygen_bits:${rsa_bits}"
elif [ "${key_type}" == "ED25519" ]; then
  echo 'Create ED25519 Key'
  pkeyopt=""
else 
  echo 'Key Type not found'
fi

############################################################
#   Backup existing certs and create dir structure
############################################################

# if our user certs dir already exists, rename it so we don't overwrite anything important
# but if it doesn't, then redirect the 'No such file or directory' error to null
time_stamp=$(date +"%Y-%m-%d_%H-%M")
if [ -d "$mosquitto_dir/certs/clients/$2" ]; then
  if [ ! -d "$mosquitto_dir/certs/old_clients" ]; then
    mkdir $mosquitto_dir/certs/old_clients
  elif [ -d "$mosquitto_dir/certs/old_clients/$2" ]; then
    rm -r $mosquitto_dir/certs/old_clients/$2
  fi
  mv $mosquitto_dir/certs/clients/$2 $mosquitto_dir/certs/old_clients/
fi

mkdir -p $mosquitto_dir/certs/clients/$2


############################################################
#   Create the key in the requested format
############################################################

openssl genpkey \
$algorithm $pkeyopt \
-outform $format_type \
-out $mosquitto_dir/certs/clients/$2/$2_key.$format_type


############################################################
#   Create the cert signing request
############################################################

openssl req \
-new \
-nodes \
-key $mosquitto_dir/certs/clients/$2/$2_key.$format_type \
-subj "/CN=$2" \
-out $mosquitto_dir/certs/clients/$2/$2_req.csr


printf '\n\n'
echo "#######################################################################"
printf '\n\n'

############################################################
#   Cert signing and creation
############################################################

openssl x509 \
-req \
-in $mosquitto_dir/certs/clients/$2/$2_req.csr \
-CA $mosquitto_dir/certs/CA/ca_crt.pem \
-CAkey $mosquitto_dir/certs/CA/ca_key.pem \
-CAcreateserial \
-out $mosquitto_dir/certs/clients/$2/$2_crt.$format_type -outform $format_type -days $days

printf '\n\n'
echo "#######################################################################"
printf '\n\n'

############################################################
#   Check the cert
############################################################

printf '\n'
printf '#   This is your new client certificate\n\n\n'

openssl x509 -text -in $mosquitto_dir/certs/clients/$2/$2_crt.$format_type -noout

printf '\n\n'
echo "#######################################################################"
printf '\n\n'

############################################################
#   Housekeeping
############################################################

#Change the permissions on the key file to give read access so that whatever we need it for can read it
chmod 644 $mosquitto_dir/certs/clients/$2/$2_key.$format_type

#clean up after the client cert creation
mv -f $mosquitto_dir/certs/clients/$2/$2_req.csr $mosquitto_dir/certs/csr_files

# copy ca_crt.{der,pem} in the required format to the new client dir
cp $mosquitto_dir/certs/clients/ca_crt.$format_type $mosquitto_dir/certs/clients/$2


echo "#   Here are the client files"

ls -bl $mosquitto_dir/certs/clients/$2

printf '\n\n'

echo "#######################################################################"
