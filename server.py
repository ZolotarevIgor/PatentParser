from http.server import BaseHTTPRequestHandler, HTTPServer
import codecs
import json
import lxml.html as html
import urllib.request

def GetURL(url):
    s = 'error'
    try:
        f = urllib.request.urlopen(url)
        s = f.read()
    except urllib.error.HTTPError:
        s = 'connect error'
    except urllib.error.URLError:
        s = 'url error'
    return s

#CN - страна, patentNum - номер категории патента 
def GetTable(CN,patentNum):
    page = GetURL(r"http://www.wipo.int/ipstats/en/statistics/country_profile/profile.jsp?code="+CN)
    tree = html.fromstring(page)
    rows = []
    xpath = '''
                //tr[@style="mso-yfti-irow:%d"]/td/table
                    /tr[@style="mso-yfti-irow:%d%s"]
                        /td/p/span/text()
            '''
    for i in range(1,11):
        s = ""
        if i == 10:
            s = ";mso-yfti-lastrow:yes"
        row = tree.xpath(xpath % (patentNum,i,s))
        row = row[0:4] #выбираем неповторяющиеся данные
        for j in range(0,4):
            if row[j] == '\u00a0':
                row[j] = 0
            else:
                row[j] = int(row[j].replace(',',''))
        rows.append(row)
    return rows

def ToJSON(_map):
    f = open("patent.json", "w")
    f.write(json.dumps(_map))#, indent = 4) )

def DataAnalysis(CountryName, Param, Year = None, Patent = 4):
    switchCase = {
        'R' : lambda j: j[1],
        'N' : lambda j: j[2],
        'A' : lambda j: j[3],
        'A/R' : lambda j: j[3] / j[1],
        'A/N' : lambda j: j[3] / j[2],
        'R/A' : lambda j: j[1] / j[3],
        'R+N' : lambda j: j[1] + j[2],
        'N/R' : lambda j: j[2] / j[1],
        'N/A' : lambda j: j[2] / j[3],
        'A/(R+N)' : lambda j : j[3] / (j[1] + j[2]), 
        '(R+N)/A' : lambda j : (j[1] + j[2]) / j[3]
    }
    #firstYear = Year[0]
    #lastYear = Year[-1]
    data = []
    count = 0
    for i in CountryName:
        tempdata = GetTable(i, Patent)
        data.append({"name":i})
        for j in tempdata:
            k = j[0] # Year
            #if k >= firstYear and k <= lastYear:
            try:
                data[count][ 'y'+str(k) ] = switchCase[Param](j)
            except ZeroDivisionError:
                data[count][ 'y'+str(k) ] = None
            #else:
            #    break
        count+=1
    return {"countries":data}

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        if self.path[-2:] == 'js':
            self.send_header('Content-type','text/javascript')
        elif self.path[-3:] == 'css':
            self.send_header('Content-type','text/css')
        elif self.path[-3:] == 'ico':
            self.send_header('Content-type', 'image/x-icon')
        else:
            self.send_header('Content-type','text/html')
        self.end_headers()
        '''if self.path[0]=='/':
            self.path = self.path[1:]'''
        if self.path == '':
            self.path = '/index.html'
            
        # Send message back to client
        message = codecs.open( self.path[1:], "r", "utf-8" ).read()
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        
        content_length = int(self.headers['Content-Length']) # <-— Gets the size of data
        post_data = self.rfile.read(content_length) # <-— Gets the data itself
        data = json.loads(post_data)
        #print(data["param"])
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        CNs = data["countries"]
        Param = data["param"]
        cdata = DataAnalysis(CountryName = CNs, Param = Param)
        message = json.dumps(cdata)
        
        # Send message back to client
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        ToJSON(cdata)
def run():
    try:
        print('starting server...')
        # Server settings
        # Choose port 8080, for port 80, which is normally used for a http server, you need root access
        server_address = ('127.0.0.1', 8080)
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        httpd.socket.close()


run()

