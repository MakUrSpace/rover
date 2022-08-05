from machine import Pin, PWM
from HTTPServer import http_daemon, build_response, build_image_response


class RoverMotorInterface:
    motorPositions = ["chest", "leftShoulder", "rightShoulder", "belly"]

    def __init__(self, chest=0, leftShoulder=1, rightShoulder=4, belly=6):
        self.chest = Pin(chest, Pin.OUT)
        self.leftShoulder = Pin(leftShoulder, Pin.OUT)
        self.rightShoulder = Pin(rightShoulder, Pin.OUT)
        self.belly = Pin(belly, Pin.OUT)
        self.pins = [self.chest, self.leftShoulder, self.rightShoulder, self.belly]
        for pin in self.pins:
            pin.value(0)

        self.chestPWM = PWM(self.chest)
        self.leftShoulderPWM = PWM(self.leftShoulder)
        self.rightShoulderPWM = PWM(self.rightShoulder)
        self.bellyPWM = PWM(self.belly)
        self.pwms = [self.chestPWM, self.leftShoulderPWM, self.rightShoulderPWM, self.bellyPWM]
        for pwm in self.pwms:
            pwm.freq(500)
            pwm.duty(0)

    def motorPositionToIndex(self, motorPosition):
        try:
            return self.motorPositions.index(motorPosition) \
                if type(motorPosition) is str else \
                int(motorPosition)
        except Exception as e:
            raise Exception("Unrecognized Motor: {}".format(motorPosition))

    def motorOn(self, motorPosition, powerLevel):
        if (motorPosition not in self.motorPositions) \
                if type(motorPosition) is str else \
                (motorPosition not in range(4)):
            raise Exception("Unrecognized Motor: {}".format(motorPosition))
        powerLevel = int(max(0, min(1, powerLevel)) * 1023)
        motorPosition = self.motorPositions.index(motorPosition) \
                        if type(motorPosition) is str else \
                        motorPosition
        self.pwms[motorPosition].duty(powerLevel)

    def motorOff(self, motor):
        if motor not in range(1, 5):
            raise Exception("Unrecognized Motor: {}".format(motor))
        self.pwms[motor].duty(0)

