from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
session.query(Restaurant).delete()
rest = Restaurant(name = "B-Bop's", city = "Des Moines")
session.add(rest)
rest = Restaurant(name = "McDonald's", city = "Des Moines")
session.add(rest)
rest = Restaurant(name = "Mars Cafe", city = "Des Moines")
session.add(rest)
session.commit()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                session = DBSession()
                results = session.query(Restaurant).all()
                output = ""
                output += "<body><html>"
                output += "<a href=""restaurants/new"" > Make a New Restaurant </a>"
                for res in results:
                    output += "<p>"+res.name+"</p>"
                    output += "<a href="+"'"+str(res.id)+"/edit' > Edit</a>"
                    output += "<a href="+"'"+str(res.id)+"/delete' > Delete</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<body><html>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Create New Restaurant</h2><input name="namerest" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                id = self.path.split("/")[1]
                output = ""
                output += "<body><html>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/'''+id+'''/edit'><h2>Edit</h2><input name="namerest" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                id = self.path.split("/")[1]
                output = ""
                output += "<body><html>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/'''+id+'''/delete'><h2>Delete</h2><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/edit"):
                id = int(self.path.split("/")[1])
                session = DBSession()
                rest = session.query(Restaurant).filter_by(id = id).one()
                if rest!=[]:
                    ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        namerest = fields.get('namerest')
                    rest.name = namerest[0]
                    logging.warning(namerest[0])
                    session.add(rest)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith("/delete"):
                id = int(self.path.split("/")[1])
                session = DBSession()
                rest = session.query(Restaurant).filter_by(id = id).one()
                if rest!=[]:
                    session.delete(rest)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    namerest = fields.get('namerest')
                session = DBSession()
                rest = Restaurant(name = namerest[0], city = "DM")
                session.add(rest)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
