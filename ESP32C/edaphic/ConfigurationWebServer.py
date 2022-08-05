from machine import reset, Timer
from HTTPServer import parse_querystring, failure, success, http_daemon
from device_utilities import get_device_sid, log_message
import json


def landing_endpoint(**kwargs):
    with open("configuration.html", "r") as f:
        html = f.read()

    if 'message' in kwargs:
        message = kwargs['message']
    else:
        message = ''

    html = html.format(device_sid=get_device_sid(), message=message)

    return html


def reset_handler(*args, **kwargs):
    log_message("Reseting device")
    reset()


def configure_form_endpoint(**kwargs):
    try:
        log_message("Decoding credentials")
        body = parse_querystring(kwargs['body'])
        ssid = body['ssid']
        password = body['password']
    except Exception as e:
        log_message("Malformed request: {}".format(e))
        return failure

    try:
        configuration = {}
        configuration['ssid'] = ssid
        configuration['password'] = password
        log_message("Storing configuration: {}".format(configuration))
        with open("configuration.json", "w") as f:
            f.write(json.dumps(configuration))

        log_message("Configuration successful. Returning successful response and resetting in 5 seconds")
        # Schedule reset
        Timer.Alarm(handler=reset_handler, s=5)
        return success

    except Exception as e:
        log_message("Failed to configure network settings: {}".format(e))
        return landing_endpoint(message="Provided Configuration Failed: {}".format(e))


path_to_handler = {
    "/": landing_endpoint,
    "/configure_form": configure_form_endpoint
}


def jormunitor_server_daemon():
    return http_daemon(ssid="Jormunitor-{}".format(get_device_sid()),
                       path_to_handler=path_to_handler)
