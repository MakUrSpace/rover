from machine import Pin, PWM


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
            parsedMotorPosition = self.motorPositions.index(motorPosition) \
                if type(motorPosition) is str else \
                int(motorPosition)
            if parsedMotorPosition not in range(4):
                raise Exception("Out of Range")
            return parsedMotorPosition
        except Exception as e:
            raise Exception("Unrecognized Motor: {}".format(motorPosition))

    def motorOn(self, motorPosition, powerLevel):
        motorPosition = self.motorPositionToIndex(motorPosition)
        powerLevel = int(max(0, min(1, powerLevel)) * 1023)
        motorPosition = self.motorPositions.index(motorPosition) \
                        if type(motorPosition) is str else \
                        motorPosition
        self.pwms[motorPosition].duty(powerLevel)

    def motorOff(self, motor):
        motor = self.motorPositionToIndex(motor)
        self.pwms[motor].duty(0)

    def allOff(self):
        for motor in self.pwms:
            motor.duty(0)

