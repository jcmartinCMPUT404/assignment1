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
        self.headers = self.data.split('\n')
        self.method, self.file_name = self.headers[0].split()[0], self.headers[0].split()[1] 
        # if header is get then go on 
        if self.method == "GET":
            response = self.process_file_name(self.file_name)
        # if header is anything else return 405 Method not allowed
        else:
            response = 'HTTP/1.0 405 Method Not Allowed'
        self.request.sendall(response.encode())
            
    def process_file_name(self, file_name):
        # if the path doesn't end with / but it's a folder, redirect
        if not file_name.endswith('/') and self.is_folder(file_name):
            return f'HTTP/1.0 301 Moved Permanently\nLocation: http://127.0.0.1:8080{file_name}/\n\n'
        # if the file ends with a / default to finding the index.html file in that folder
        if file_name.endswith('/'):
            file_name = file_name + 'index.html'
        try:
            fin = open('.'+file_name)
            content = fin.read()
            fin.close()
            return 'HTTP/1.0 200 OK\n' + self.get_mime_type(file_name) + content
        except:
            return 'HTTP/1.0 404 Not FOUND\n\n'

    def is_folder(self, file_name):
        # it doesn't end with an extension
        last_section = file_name.split('/')[-1]
        if len(last_section.split('.')) == 1:
            return True
        return False
    
    def get_mime_type(self, file_name):
        if file_name.endswith('.html'):
            return 'Content-Type: text/html\n\n'
        elif file_name.endswith('.css'):
            return 'Content-Type: text/css\n\n'
        else:
            return 'Content-Type: text/plain\n\n'

if __name__ == "__main__":
    os.chdir('./www')
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
