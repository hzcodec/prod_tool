WINDOW_SIZE = (1035, 870)

TEXT_SERIAL_PORT_BORDER = 10

HEADLINE = 70*' '+'Production Test Tool, ACX/TCX'
MSG_QUIT = 'Quit application?\n\nCheck that Ascender motor has stopped!\n'


# misc colors
RED   = (255, 0 , 0)
GREY  = (180, 180, 180)
BLACK = (0, 0, 0)
WHITE   = (255, 255, 255)
GREEN = (36, 119, 62)



# time delays in seconds
DELAY_05 = 0.5
DELAY_03 = 0.3
DELAY_1  = 1.0


# max/min motor speed
MOTOR_SPEED = 80


class Port(object):
    PORT_NOT_AVAILABLE = 0
    PORT_AVAILABLE = 1
