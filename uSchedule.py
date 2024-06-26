import json
import wifi
import socketpool
import microcontroller

def internetConnect(ssid, password):
    print("connecting")
    wifi.radio.connect(ssid, password)
    print("connected")
    pool = socketpool.SocketPool(wifi.radio)
    

    print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
    print("My IP address is", wifi.radio.ipv4_address)
    return pool

class uTime:
    def __init__(self, t_str):
        # t_str is a string that has the time as "9:30[]:00]"
        t = t_str.split(":")
        self.hr = int(t[0])
        self.min = int(t[1])
        self.totMins = self.hr * 60 + self.min
        if len(t) == 3:
            self.sec = int(t[2])
        else:
            self.sec = 0
        self.totSecs = self.totMins * 60 + self.sec

    def __str__(self):
        return f'{self.hr}:{str(self.min)}:{str(self.sec)}'


class period:
    def __init__(self, startTime, endTime, note=""):
        # enter start and end times as strings "00:00[:00]"
        self.startTime = uTime(startTime)
        self.endTime = uTime(endTime)
        self.note = note
        self.lengthInSeconds = self.endTime.totSecs - self.startTime.totSecs

    def __str__(self):
        t = f'{self.startTime}-{self.endTime}'
        return t


class daySchedule:
    def __init__(self, dayName, periods):
        self.dayName = dayName
        self.periods = periods

        # (todo) Check that periods do not overlap
    def findPeriod(self, t="00:00:00"):
        t = uTime(t)
        # p = -1
        if (t.totSecs < self.periods[0].startTime.totSecs):
            # before periods
            return period("00:00", f"{self.periods[0].startTime}", "Before Periods")
        elif (t.totSecs >= self.periods[-1].endTime.totSecs):
            # after periods
            return period(f"{self.periods[-1].endTime}", "23:59:59", "After Periods")
        for i in range(len(self.periods)):
            # check if in a period
            if ((t.totSecs > self.periods[i].startTime.totSecs) and (t.totSecs <= self.periods[i].endTime.totSecs)):
                # p = i
                return self.periods[i]
            # check if in between periods:
            if ((t.totSecs > self.periods[i-1].endTime.totSecs) and (t.totSecs <= self.periods[i].startTime.totSecs)):
                return period(f'{self.periods[i-1].endTime}', f"{self.periods[i].startTime}", "Passing Time")
        # if nothing found
        return None


def calcTime(requests, daySchedules, timeURL):
    localTime, today = getLocalTime(requests, timeURL)
    print(localTime, today)
    p = daySchedules[today].findPeriod(f'{localTime}')
    print(p)
    timeLeft = p.endTime.totSecs - localTime.totSecs
    if timeLeft != 0:
        fracDone = (localTime.totSecs - p.startTime.totSecs) / timeLeft
    else:
        fracDone = 100
    print(timeLeft, fracDone)
    return (timeLeft, p)


def getLocalTime(requests, url='http://makerspace.local/makerspaceTime.php'):
    
    try:
        response = requests.get(url)
        timeStr = response.text
        response.close()
        t = json.loads(timeStr)
        # lt = time.strptime(f'{t["tm_year"]+1900}', '%Y')
        lt = f'{t["tm_hour"]}:{t["tm_min"]}:{t["tm_sec"]}'
        return (uTime(lt), t['tm_wday'])
    except Exception as e:
        print("Error:\n", str(e))
        microcontroller.reset()

