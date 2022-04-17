import subprocess
import io
from flask import Response, Flask, request
from prometheus_client import Counter, Summary, Gauge, Histogram, generate_latest

from typing import Optional

class Tester():
    def __init__(self):
        pass
    def Read(self, arglist:Optional[list]=[]):
        proc = subprocess.Popen(["speedtest", "--accept-license", "-f", "json"]+arglist, stdout=subprocess.PIPE)
        proc.poll()

        text = ""
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            text = text+line
        try:
            import json
            data = json.loads(text)
            return data
        except json.decoder.JSONDecodeError:
            return dict()
    def MakeTest(self, id:Optional[str]=0, host:Optional[str]='', interface:Optional[str]='', ip:Optional[str]='') -> dict:
        req = []
        if not (id=="" or id==None):
            req = req+['-s', str(id)]
        elif not (host=="" or host==None):
            req = req+['-o', str(host)]
        if not (interface=="" or interface==None):
            req = req+['-I', str(interface)]
        elif not (ip=="" or ip==None):
            req = req+['-i', str(ip)]
        return self.Read(req)
    def ListServer(self) -> dict:
        return self.Read(["--servers"])

def Converter(self, data: dict, name:Optional[str]="speedtest") -> str:
    answer = ""
    # name processing
    if name == None or name == "":
        name = ""
    else:
        if name[-1]!="_":
            name = name+"_"
    name_ = name.replace(" ", "")
        
    for key in data.keys():
        if type(data[key]) is dict:
            answer = answer+self.Converter(data[key], name+key)
        elif type(data[key]) is list:
            for ele in data[key]:
                answer = answer+self.Converter(ele, name+key)
        else:
            if(name_ != ""):
                answer = answer + "%s%s\t%s\n"%(name_, key, data[key])
            else:
                answer = answer + "%s\t%s\n"%(key, data[key])
        return answer


app = Flask(__name__)

ping_latency_gauge = Gauge('latency', 'Result of latency on ping test',
                            namespace='speedtest', unit='seconds')
ping_jitter_gauge  = Gauge('jitter' , 'Result of jitter on ping test',
                            namespace='speedtest', unit='seconds')

speed_types           = ['upload', 'download']
speed_bandwidth_gauge = Gauge('bandwidth', 'Result of bandwidth on speed test', ['type'],
                              namespace='speedtest', unit='byteseconds')
speed_bytes_gauge     = Gauge('bytes'            , 'Result of bytes on speed test'    , ['type'],
                              namespace='speedtest', unit='bytes')
speed_elapsed_gauge   = Gauge('elapsed'        , 'Result of elapsed on speed test'  , ['type'],
                              namespace='speedtest', unit='seconds')

interface_types    = ['internalIp', 'name', 'macAddr', 'isVpn', 'externalIp']
interface_gauge    = Gauge('interface', 'Interface Information', interface_types, namespace='speedtest')

server_types       = ['id', 'host', 'port', 'location', 'country']
server_gauge       = Gauge('server', 'Server Informations', server_types, namespace='speedtest')

gauges = [ping_latency_gauge, ping_jitter_gauge, speed_bandwidth_gauge,
          speed_bytes_gauge, speed_elapsed_gauge, interface_gauge, server_gauge]

def speedtest(id:Optional[int]=0, host:Optional[str]='', interface:Optional[str]='', ip:Optional[str]=''):
    # for gauge in gauges:
    #     Gauge.clear(gauge)
    # ping_latency_gauge.clear()
    # ping_jitter_gauge.clear()
    speed_bandwidth_gauge.clear()
    speed_bytes_gauge.clear()
    speed_elapsed_gauge.clear()
    speed_bandwidth_gauge.clear()
    speed_bytes_gauge.clear()
    speed_elapsed_gauge.clear()

    a = Tester()
    data = a.MakeTest(id=id, host=host, interface=interface, ip=ip)

    ping_latency_gauge.set(data['ping']['latency']*0.001)
    ping_jitter_gauge.set(data['ping']['jitter']*0.001)

    speed_bandwidth_gauge.labels('upload').set(data['upload']['bandwidth'])
    speed_bytes_gauge.labels('upload',).set(data['upload']['bytes'])
    speed_elapsed_gauge.labels('upload').set(data['upload']['elapsed'])

    speed_bandwidth_gauge.labels('download').set(data['download']['bandwidth'])
    speed_bytes_gauge.labels('download',).set(data['download']['bytes'])
    speed_elapsed_gauge.labels('download').set(data['download']['elapsed'])


    interface_gauge.labels(data['interface']['internalIp'],
                           data['interface']['name'],
                           data['interface']['macAddr'],
                           data['interface']['isVpn'],
                           data['interface']['externalIp']).set(1.0)

    server_gauge.labels(data['server']['id'],
                        data['server']['host'],
                        data['server']['port'],
                        data['server']['location'],
                        data['server']['country']).set(1.0)
    pass

@app.route("/metrics/", methods=["GET"])
def metrics():
    print(request.args)
    speedtest(request.args.get('id'), request.args.get('host'), request.args.get('interface'), request.args.get('ip'))
    result = []
    for gauge in gauges:
        result.append(generate_latest(gauge))
    return Response(result, mimetype="text/plain")

@app.route("/servers", methods=["GET"])
def servers():
    a = Tester()
    data = a.ListServer()
    server_gauge.clear()

    serverlist = data['servers']

    for ele in serverlist:
        server_gauge.labels(ele['id'],ele['host'],ele['port'],ele['location'],ele['country']).set(1.0)

    result = [ generate_latest(server_gauge) ]
    return Response(result, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True, port=9516)