#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).decode()
        self.headers = self.data.split('\r\n')
        for each in self.headers:
            if each.startswith("Host:"):
                self.host = each.split(": ")[-1]
        self.method, self.file_name = self.headers[0].split()[0], self.headers[0].split()[1]
        # if header is get then go on 
        if self.method == "GET":
            response = self.process_file_name()
        # if header is anything else return 405 Method not allowed
        else:
            response = 'HTTP/1.1 405 Method Not Allowed'
        self.request.sendall(response.encode())
            
    def process_file_name(self):
        # if it is a folder but it's missing a slash, redirect
        if os.path.isdir(self.file_name[1:]) and not self.file_name.endswith('/'):
            return f'HTTP/1.1 301 Moved Permanently\r\nLocation: http://{self.host + self.file_name}/\r\n\r\n'
        # if the file ends with a / default to finding the index.html file in that folder
        if self.file_name.endswith('/'):
            self.file_name += 'index.html'
        try:
            if self.is_malicious():
                raise Exception("Malicious")
            fin = open('.'+self.file_name)
            content = fin.read()
            fin.close()
            return 'HTTP/1.1 200 OK\r\n' + self.get_mime_type() + content
        except:
            return 'HTTP/1.1 404 Not FOUND\r\n\r\n'

    def is_malicious(self):
        current_level = 0
        folder_parse = self.file_name.split('/')
        for each in folder_parse:
            if each == "..":
                current_level -= 1
            elif each == ".":
                continue
            else:
                current_level += 1
                
            if current_level < 0:
                return True
        return False

    def get_mime_type(self):
        if self.file_name.endswith('.html'):
            return 'Content-Type: text/html\r\n\r\n'
        elif self.file_name.endswith('.css'):
            return 'Content-Type: text/css\r\n\r\n'
        else:
            return 'Content-Type: text/plain\r\n\r\n'

if __name__ == "__main__":
    os.chdir('./www')
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
