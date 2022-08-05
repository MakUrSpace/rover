from HTTPServer import http_daemon, build_response, build_image_response


class RoverServer:
    def __init__(self, roverMotorInterface):
        self.roverMotorInterface = roverMotorInterface

    def servePage(self, pageMessage='', **request):
        with open("rover.html", "r") as f:
            page = f.read()
        page = page.replace('{pageMessage}', pageMessage)
        return build_response(body=page)

    def motorHandler(self, **request):
        motorPosition = request['path'].split('/')[1]
        motorPosition = self.roverMotorInterface.motorPositionToIndex(motorPosition)
        requestedAction = request['path'].split('/')[2]
        if requestedAction not in ['on', 'off']:
            raise Exception('Unrecognized action: {}'.format(requestedAction))

        powerLevel = 0.5 if requestedAction == 'on' else 0
        self.roverMotorInterface.motorOn(motorPosition, powerLevel)

        return self.servePage()

    def commandHandler(self, **request):
        self.roverMotorInterface.allOff()
        commands = {
            "reward": ["chest", "leftShoulder", "rightShoulder", "belly"],
            "sit": ["belly"],
            "come": ["chest"],
            "off": []
        }

        command = request['path'].split('/')[2]
        if command not in commands:
            raise Exception('Unrecognized command: {}'.format(command))

        for motorPosition in commands[command]:
            motorPosition = self.roverMotorInterface.motorPositionToIndex(motorPosition)
            self.roverMotorInterface.motorOn(motorPosition, 0.5)

        return self.servePage(pageMessage='{} command activated...'.format(command[0].upper() + command[1:]))

    def openServer(self):
        http_daemon(path_to_handler={
          "/": self.servePage,
          "/command/reward": self.commandHandler,
          "/command/sit": self.commandHandler,
          "/command/come": self.commandHandler,
          "/command/off": self.commandHandler
        })
