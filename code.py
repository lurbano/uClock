import time
import ssl

import adafruit_requests
from uSchedule import *
from ledPixelsPico import *

nPix = 72
#ledPix = ledPixels(nPix, board.GP18)

try:
    from ledPixelsPico import *
    ledPix = ledPixels(nPix, board.GP18)
except:
    print("ledPix not active")
    
colMag = 10     # Color magnitude
doneColor = (colMag, 0, 0)
togoColor = (0, colMag, 0)
passColor = (0, 0, colMag)
passDoneColor = (colMag/2, 0, colMag/2)

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
asch = period("15:35", "16:00", "After School")

tha = period("12:45", "12:55", "Afternoon Advisory (Thurs)")

fm = period("8:00", "9:15", "Faculty Meeting")
th1 = period("9:15", "9:55", "First Period (Thurs)")
th2 = period("10:00", "10:40", "Second Period (Thurs)")
th3 = period("10:45", "11:25", "Third Period (Thurs)")
thLong = period("13:00", "14:40", "Long Period (Thurs)")

# daily schedules
daySchedules = [
    daySchedule("Sunday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
    daySchedule("Monday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea, asch]),
    daySchedule("Tuesday", [m0, ma, m1, m2, m3, em, lunch, a1, a2, ea, asch]),
    daySchedule("Wednesday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea, asch]),
    daySchedule("Thursday", [fm, th1, th2, th3, em, lunch, tha, thLong, ea, asch]),
    daySchedule("Friday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea, asch]),
    daySchedule("Saturday", [m0, mm, m1, m2, m3, em, lunch, a1, a2, ea]),
]




print(daySchedules[1].dayName)
print(daySchedules[1].findPeriod("12:15:01"))

# connect to wifi
pool = internetConnect("TFS Students", "Fultoneagles")
requests = adafruit_requests.Session(pool, ssl.create_default_context())

while True:
    (secsToGo, currentPeriod) = calcTime(requests, daySchedules)
    print(f"{currentPeriod.note}: {currentPeriod}")
    if (currentPeriod.note == "Passing Time"):
        leftColor, elapsedColor = (colMag, colMag, 0), (0, colMag, colMag)
    elif (currentPeriod.note == "Before Periods" or currentPeriod.note == "After Periods"):
        leftColor, elapsedColor = (colMag, colMag, 0), (0, colMag, colMag)
    else:
        leftColor, elapsedColor = doneColor, togoColor
    startTime = time.monotonic()
    dt = 0
    while (dt < secsToGo):
        frac = (secsToGo-dt) / currentPeriod.lengthInSeconds
        print(f'{currentPeriod} | {secsToGo-dt}s Left: {(secsToGo-dt)/60}/{currentPeriod.lengthInSeconds/60} | {frac*100}%')
        
        nLights = min(int(frac*nPix), nPix)
        print("+"*nLights,"-"*(nPix-nLights))
        #leftColor = doneColor
        #elapsedColor = togoColor
        ledPix.twoColorsTimestep(nLights, elapsedColor, leftColor, 0.01)
        
        time.sleep(2)
        dt = (time.monotonic() - startTime)

