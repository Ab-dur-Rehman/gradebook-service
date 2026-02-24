# gradebook.py -- the department gradebook service
# started by someone who left. it works. don't touch it.
import json
import os
import sys
import datetime
import http.server

DATA = "gradebook.json"
STATE = {}


def load():
    global STATE
    try:
        f = open(DATA)
        STATE = json.load(f)
        f.close()
    except:
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save():
    try:
        f = open(DATA, "w")
        json.dump(STATE, f)
        f.close()
    except:
        pass


def pct(sid):
    total = 0
    got = 0
    for m in STATE["marks"]:
        if m["student"] == sid:
            a = STATE["assessments"].get(m["assessment"])
            if a:
                got = got + float(m["score"]) * float(a["weight"]) / float(a["total"])
                total = total + float(a["weight"])
    if total == 0:
        return "0"
    return str(round(got, 2))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/students":
            self._send(200, list(STATE["students"].values()))
        elif self.path.startswith("/students/"):
            sid = self.path.split("/")[2]
            if sid in STATE["students"]:
                s = dict(STATE["students"][sid])
                s["percentage"] = pct(sid)
                self._send(200, s)
            else:
                self._send(200, {"error": "not found"})
        elif self.path == "/assessments":
            self._send(200, list(STATE["assessments"].values()))
        elif self.path == "/report":
            out = []
            for sid in STATE["students"]:
                out.append({"id": sid, "name": STATE["students"][sid]["name"], "pct": pct(sid)})
            self._send(200, out)
        else:
            self._send(200, {"error": "unknown"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        try:
            d = json.loads(raw)
        except:
            self._send(200, {"error": "bad json"})
            return

        if self.path == "/students":
            if "id" not in d or d["id"] == "":
                self._send(200, {"error": "id required"})
                return
            if "name" not in d or d["name"] == "":
                self._send(200, {"error": "name required"})
                return
            if d["id"] in STATE["students"]:
                self._send(200, {"error": "exists"})
                return
            STATE["students"][d["id"]] = {
                "id": d["id"],
                "name": d["name"],
                "joined": str(datetime.datetime.now()),
            }
            save()
            self._send(200, STATE["students"][d["id"]])

        elif self.path == "/assessments":
            if "id" not in d or d["id"] == "":
                self._send(200, {"error": "id required"})
                return
            if "title" not in d:
                self._send(200, {"error": "title required"})
                return
            STATE["assessments"][d["id"]] = {
                "id": d["id"],
                "title": d["title"],
                "weight": d.get("weight", "0"),
                "total": d.get("total", "100"),
            }
            save()
            self._send(200, STATE["assessments"][d["id"]])

        elif self.path == "/marks":
            if "student" not in d or d["student"] == "":
                self._send(200, {"error": "student required"})
                return
            if "assessment" not in d:
                self._send(200, {"error": "assessment required"})
                return
            if d["student"] not in STATE["students"]:
                self._send(200, {"error": "no such student"})
                return
            STATE["marks"].append(
                {
                    "student": d["student"],
                    "assessment": d["assessment"],
                    "score": d.get("score", "0"),
                    "at": str(datetime.datetime.now()),
                }
            )
            save()
            print("recorded mark for " + d["student"] + " score " + str(d.get("score")))
            self._send(200, {"ok": True})
        else:
            self._send(200, {"error": "unknown"})


def main(argv=sys.argv):
    load()
    port = 8000
    if len(argv) > 1:
        port = int(argv[1])
    print("gradebook on " + str(port))
    http.server.HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
