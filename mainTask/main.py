import network
import machine
import usocket as socket

# Initialize the LED pin
led = machine.Pin(16, machine.Pin.OUT)

def start_ap():
    ssid = 'test_server'
    password = '12345678'

    ap= network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(ssid=ssid, key=password)

    while ap.active() == False:
        pass

    print('Ap started')

# Define the HTTP response with headers
def http_response(status_code, content_type, content):
    return "HTTP/1.1 {} OK\r\nContent-Type: {}\r\n\r\n{}".format(status_code, content_type, content)

# Define the HTTP request handler function
def handle_request(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    
    # Check if the request is a GET request and for the root ("/")
    if "GET / " in request_data:
        try:
            # Read and send the HTML content from the file
            with open("index.html", "r") as html_file:
                html_content = html_file.read()
            response = http_response(200, "text/html", html_content)
        except OSError:
            response = http_response(500, "text/plain", "Error reading HTML file")
    elif "GET /toggle " in request_data:
        led.value(not led.value())
        response = http_response(200, "text/plain", "LED toggled")
    else:
        response = http_response(404, "text/plain", "Not Found")

    client_socket.send(response)
    client_socket.close()

def start_server():
    # Create a socket, bind it to port 80, and start listening
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)

    print("Web server started")

    while True:
        client_socket, addr = server_socket.accept()
        handle_request(client_socket)

    