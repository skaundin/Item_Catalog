from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                url_for()
                self.wfile.write(output)
                print(output)
                return
        except IOError:
            self.send_error(404, "File not found %s", self.path)


def main():

    try:
        port = 5000
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered stopping server")
        server.socket.close()


if __name__ == '__main__':
    main()
