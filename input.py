import pygame

# platform-specific includes
try:
    from gpiozero import Button     # import gpiozero.Button if available, ie. we're running on raspi
except:
    class Button:                   # dummy class to stand in for gpiozero on non-raspi machines
        def __init__(self, x):
            self.x = x
            self.is_pressed = False


class Input:
    # gamebutton dict
    pressedKeys = []

    numJoysticks = 0

    # maybe add some configuration sometime not sure tbh fam
    # axes: 0 = vert: 1 = horiz: 2 = trig: 3 = horiz2: 4 = vert2
    # butts: a b x y lb rb back start ls rs
    #       +   -
    #   -           -
    # -   +       -   +
    #   +           +
    controllers = {

    }

    buttons = {
        'moveUp': {
            'pressed': False,
            'held': False,
            'gpio': Button(2),
            'key': pygame.K_w,
            },
        'moveLeft': {
            'pressed': False,
            'held': False,
            'gpio': Button(3),
            'key': pygame.K_a,
            },
        'moveDown': {
            'pressed': False,
            'held': False,
            'gpio': Button(4),
            'key': pygame.K_s,
            },
        'moveRight': {
            'pressed': False,
            'held': False,
            'gpio': Button(14),
            'key': pygame.K_d,
            },
        'fireUp': {
            'pressed': False,
            'held': False,
            'gpio': Button(15),
            'key': pygame.K_UP,
            },
        'fireLeft': {
            'pressed': False,
            'held': False,
            'gpio': Button(17),
            'key': pygame.K_LEFT,
            'joy': 0,
            'jaxis': 0,
            'jhat': 0,
            'jbutton': 0,
            },
        'fireDown': {
            'pressed': False,
            'held': False,
            'gpio': Button(18),
            'key': pygame.K_DOWN,
            },
        'fireRight': {
            'pressed': False,
            'held': False,
            'gpio': Button(27),
            'key': pygame.K_RIGHT,
            },
        'menu': {
            'pressed': False,
            'held': False,
            'gpio': Button(0),
            'key': pygame.K_ESCAPE,
            },
        }

    inputTypeList = [pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP,
                     pygame.MOUSEBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYHATMOTION,
                     pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN]

    @staticmethod
    def __init__():
        pygame.joystick.init()
        Input.numJoysticks = pygame.joystick.get_count()

        for i in range(Input.numJoysticks):
            pygame.joystick.Joystick(i).init()
            Input.controllers[i] = {

            }

    @staticmethod
    def update():
        events = pygame.event.get(Input.inputTypeList)

        for event in events:
            if event.type == pygame.KEYDOWN:
                Input.keydown(event.key)
            elif event.type == pygame.KEYUP:
                Input.keyup(event.key)
            elif event.type in range(pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN):
                print(vars(event))

        for b, button in Input.buttons.items():
            if button['gpio'].is_pressed or button['key'] in Input.pressedKeys:
                button['held'] = True
                if not button['pressed']:
                    button['pressed'] = True
                else:
                    button['pressed'] = False
            else:
                button['pressed'] = False
                button['held'] = False

    @staticmethod
    def keydown(key):
        if key not in Input.pressedKeys:
            Input.pressedKeys.append(key)

    @staticmethod
    def keyup(key):
        if key in Input.pressedKeys:
            Input.pressedKeys.remove(key)

    @staticmethod
    def numsticks():
        return Input.numJoysticks

    @staticmethod
    def stickinfo(i):
        if Input.numJoysticks > 0 and i in range(Input.numJoysticks):
            j = pygame.joystick.Joystick(i)
            info = {"id": j.get_id(),
                    "name": j.get_name(),
                    "numaxes": j.get_numaxes(),
                    "numballs": j.get_numballs(),
                    "numbuttons": j.get_numbuttons(),
                    "numhats": j.get_numhats()
                    }
            return info
        return False
