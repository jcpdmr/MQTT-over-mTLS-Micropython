from umqtt.simple import MQTTClient
import ussl as ssl          
import utime
import network


# wifi connection
sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
sta_if.active(True)
with open("./wifi.conf") as f:
    wifi_ssid = f.readline().split("=")[1].strip()
    wifi_ssid = wifi_ssid.strip('"')
    wifi_psw = f.readline().split("=")[1].strip()
    wifi_psw = wifi_psw.strip('"')
    server_ip = f.readline().split("=")[1].strip()  # this has to match the MQTT server CN or SAN credentials in server_crt.pem
    server_ip = server_ip.strip('"')
    server_port = f.readline().split("=")[1].strip()
    server_port = int(server_port.strip('"'))

print('Read Wifi Config... OK')

sta_if.connect(wifi_ssid, wifi_psw)

print('Trying Wifi connection')
utime.sleep(4)

if(sta_if.isconnected()):
    print('Wifi Connection... OK')
else:
    print('Wifi Connection... ERROR')


server_keepalive=60     # if you don't include a keepalive nothing works.
mqtt_topic='test/topic01'
local_client_name='client1'

# This uses the CA cert, along with a user key & cert
# TLS certs & keys need to be in DER format

with open('./certs/ca_crt.der', 'rb') as f:
    ca_data = f.read()
f.close()
print('Read CA Certificate... OK')

with open('./certs/esp_crt.der', 'rb') as f:
    user_cert = f.read()
f.close()
print('Read User Certificate... OK')

with open('./certs/esp_key.der', 'rb') as f:
    user_key = f.read()
f.close()
print('Read User Key... OK')


ssl_params={'key':user_key,
            'cert':user_cert,
            'cadata':ca_data,
            'server_hostname':server_ip,
            'server_side':False,
            'cert_reqs':ssl.CERT_REQUIRED,
            'do_handshake':True}

# we don't need username or password here
# as we use the directive 'use_identity_as_username true' in mosquitto.conf
# this takes the CN from the TLS cert and uses it as the username

def connectMQTT():
    client = MQTTClient(
        client_id=local_client_name,
        server=server_ip,
        port=server_port,
        keepalive=server_keepalive,
        ssl=True,
        ssl_params=ssl_params
    )
    
    client.connect()
    return client

def start_client():

    client = connectMQTT()
    print("Connecting to MQTT Server...")

    while True: 
        print("Sending ON") 
        client.publish(topic=mqtt_topic, msg="ON")
        utime.sleep(1) 
        print("Sending OFF") 
        client.publish(topic=mqtt_topic, msg="OFF")
        
        utime.sleep(1)