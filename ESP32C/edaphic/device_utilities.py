from time import sleep
import random
import machine
import ntptime
import os
from ubinascii import hexlify
import network


def get_timestamp(rtc=None):
    if rtc is None:
        rtc = machine.RTC().datetime()

    # for 2nd of February 2017 at 10:30am (TZ 0)
    # rtc.init((2017, 2, 28, 10, 30, 0, 0, 0))
    year = rtc[0]
    month = rtc[1]
    day = rtc[2]
    hour = rtc[3]
    minute = rtc[4]
    second = rtc[5]
    milliseconds = rtc[6]

    date_time = "{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{milliseconds:04d}Z".format(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        milliseconds=milliseconds
    )

    return date_time


def get_day_timestamp(rtc=None):
    ts = get_timestamp(rtc)
    return ts.split('T')[0].strip()


def Random():
    r = random.getrandbits(32)
    return ((r[0] << 24) + (r[1] << 16) + (r[2] << 8) + r[3]) / 4294967295.0


def get_device_sid():
    machine_byte_id = machine.unique_id()
    return hexlify(machine_byte_id).decode()


def configure_uart():
    uart = machine.UART(0, 115200)
    os.dupterm(uart)


def log_message(message):
    timestamp = get_timestamp()
    print("{:28} | {}".format(timestamp, message))


def reset_handler(*args, **kwargs):
    print("Resetting device in 5 seconds")
    sleep(5)
    machine.reset()


def simple_connect(ssid, pw, wlan=None, max_attempts=10, log=print):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    results = wlan.scan()
    chosenNetwork = None
    for result in results:
        if result[0].decode() == ssid:
            chosenNetwork = result

    if chosenNetwork is None:
        raise Exception("Network {} not found".format(ssid))

    wlan.connect(ssid, pw)
    for i in range(max_attempts):
        timeouts = 20
        for t in range(timeouts):
            if wlan.isconnected():
                break
            sleep(1)

    log("Connected")
    log(wlan.ifconfig())

    return wlan

