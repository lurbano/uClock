import time
import ssl
import ipaddress
import adafruit_requests
from uSchedule import *

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType


# periods
m0 = period("8:00", "8:15", "Before Classes")
mm = period("8:15", "8:30", "Morning Meeting")
ma = period("8:15", "8:30", "Morning Advisory")
m1 = period("8:30", "9:25", "First Period")
m2 = period("9:30", "10:25", "Second Period")
m3 = period("10:30", "11:25", "Third Period")
em = period("11:30", "12:15", "Monring Elective")
lunch = period("12:15", "12:45", "Lunch")

a1 = period("12:45", "13:40", "First Afternoon Period")
a2 = period("13:45", "14:40", "Second Afternoon Period")
ea = period("14:45", "15:30", "Afternoon Elective")

tha = period("12:45", "12:55", "Afternoon Advisory (Thurs)")

fm = period("8:00", "9:15", "Faculty Meeting")
th1 = period("9:15", "9:55", "First Period (Thurs)")
th2 = period("10:00", "10:40", "Second Period (Thurs)")
th3 = period("10:45", "11:25", "Third Period (Thurs)")
thLong = period("13:00", "14:40", "Long Period (Thurs)")

# daily schedules
daySchedules = [
    daySchedule("Sunday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Monday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Tuesday", [m0, ma, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Wednesday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Thursday", [fm, th1, th2, th3, em, lunch, tha, thLong, ea]),
    daySchedule("Friday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Saturday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
]


print(daySchedules[1].dayName)
print(daySchedules[1].findPeriod("12:15:01"))

# connect to wifi
pool = internetConnect("Wifipower", "defacto1")
requests = adafruit_requests.Session(pool, ssl.create_default_context())


server = HTTPServer(pool)

# load web page
def getWebpage():
    with open("schedule.html", "r") as f:
        html = f.read()
    return html

#  route default static IP


@server.route("/")
def base(request: HTTPRequest):  # pylint: disable=unused-argument
    #  serve the HTML
    #  with content type text/html
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:

        response.send(getWebpage())


print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")




while True:
    (secsToGo, currentPeriod) = calcTime(requests, daySchedules)
    print(f"{currentPeriod.note}: {currentPeriod}")
    startTime = time.monotonic()
    dt = 0
    while (dt < secsToGo):
        frac = (secsToGo-dt) / currentPeriod.lengthInSeconds
        print(
            f'Seconds Left: {secsToGo-dt}/{currentPeriod.lengthInSeconds} | {frac*100}%')
        sleepTime = 2
        startSleep = time.monotonic()
        while ((time.monotonic() - startSleep) < sleepTime):
            try:
                server.poll()
            except Exception as e:
                print(f'server error: {e}')
                continue

        dt = (time.monotonic() - startTime)

