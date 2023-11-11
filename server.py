from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from netmiko import ConnectHandler
import re
import random


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('home.html', 'r') as file:
                self.wfile.write(file.read().encode('utf-8'))
        elif self.path.endswith('.css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open(self.path[1:], 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'image/png')  # Adjust the content type as per your image type
            self.end_headers()
            with open(self.path[1:], 'rb') as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/configure_ssid':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_params = parse_qs(post_data)
            ssid = post_params['ssid'][0]

            device = {
            'device_type': 'cisco_ios',
            'ip': '10.1.44.105',  # IP address of the Cisco device
            'username': 'admin',
            'password': 'MFUschl123',
            'secret': 'MFUschl123',
            }



         # Connect to the Cisco device
            net_connect = ConnectHandler(**device)
            oo = net_connect.enable()
            # Send the command
            print(oo)
            
            output = net_connect.send_command("show wlan summary")



            wlan_ids = []
            lines = output.splitlines()
            print(lines)
            for line in lines[5:]:
                if line.strip():
                    match = re.match(r'^\s*(\d+)', line)
                if match:
                    wlan_id = match.group(1)
                    wlan_ids.append(wlan_id)

        # Print the WLAN IDs
            for wlan_id in wlan_ids:
                print(wlan_id)
    
            existing_array = [None] * 15

            # Your code to retrieve WLAN IDs and store them in wlan_ids list


# Add the values from wlan_ids to the existing array
            for i in range(len(wlan_ids)):
                existing_array[i] = wlan_ids[i]

# Print the updated array
            print(existing_array) 

            next_position = existing_array.index(None)

# Generate a random number between 1 and 16
            random_num = random.randint(1, 16)

# Check if the random number already exists in the array
            while str(random_num) in existing_array:
                random_num = random.randint(1, 16)  # Generate a new random number

# Replace the next available position with the random number
            existing_array[next_position] = str(random_num)

            
            
            config_commands =[
                
             f'wlan {ssid} {random_num} {ssid}',
             f'no security wpa',
             f'no shutdown',
             f'exit',
             f'wireless tag policy wlc-policy-tag',
             f'wlan {ssid} policy default-policy-profile',
             f'end',
             ]

            output = net_connect.send_config_set(config_commands)
            print(output)

            # Disconnect from the Cisco device
            net_connect.disconnect()

            self.send_response(200)
            self.end_headers()
            self.wfile.write('SSID configuration successful!'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()