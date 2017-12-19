import os
import pygame
from gameobject import *

# platform-specific includes
try:
    import gpiozero.Button as GPIOButton     # import gpiozero.Button if available, ie. we're running on raspi
except ImportError:
    class GPIOButton:                   # dummy class to stand in for gpiozero on non-raspi machines
        def __init__(self, x):
            self.x = x
            self.is_pressed = False


class Game:
    @classmethod
    def __init__(cls, **settings):
        cls.debug = True

        # basic game settings + defaults
        cls.settings_default = {'fullscreen': False,
                                'fps': 60,
                                'window_size': (1024, 768),
                                'game_name': 'top game',
                                'game_version': 1, 'game_subtitle': 'biscuit',
                                'game_caption': ''}
        cls.settings = cls.settings_default
        cls.settings['window_size_half'] = (int(cls.settings['window_size'][0]/2), int(cls.settings['window_size'][1]/2))
        cls.surface = False
        cls.fonts = {}
        cls.fps_clock = pygame.time.Clock()
        cls.quit = False

        cls.input_initialized = False

        # game paths/data files
        # base = path to game exe
        # data = datadir subdir with common data files
        # img = image subdir
        # mod = datadir subdir with mod files
        cls.dir_base = os.path.split(os.path.abspath(__file__))[0]
        cls.dir_data = os.path.join(cls.dir_base, 'data')
        cls.dir_img = os.path.join(cls.dir_data, 'img')
        cls.dir_mod = os.path.join(cls.dir_base, 'mods')

        # game object prototype dictionary
        cls.gameobject_prototypes = {}

        # modules
        cls.object_manager = ObjectManager(cls.gameobject_prototypes)

        # scenes
        cls.scenes = {}

        # menus
        cls.menus = {}

        # event lists
        cls.events_video = []
        for e in range(pygame.VIDEORESIZE, pygame.VIDEOEXPOSE + 1):
            cls.events_video.append(e)

        # todo: get/set settings from file
        for item, value in settings.items():
            cls.settings[item] = value

        pygame.mouse.set_visible(False)
        cls.rebuild_surface()
        cls.set_caption()
        cls.fonts['default'] = pygame.font.Font('freesansbold.ttf', 16)

        # init modules
        cls.init_input()

        # settings test
        print(cls.settings['game_caption'])
        for i in range(len(cls.settings['game_caption'])):
            print('/', end='')
        print('')
        for n, val in cls.settings.items():
            print(str(n) + "> " + str(val))

    @classmethod
    def shutdown(cls):
        pygame.quit()

    @classmethod
    def rebuild_surface(cls):
        cls.surface = pygame.display.set_mode(cls.settings['window_size'], cls.settings['fullscreen'])

    @classmethod
    def set_caption(cls):
        cls.settings['game_caption'] = "{} v{} - {} ".format(cls.settings['game_name'],
                                                 cls.settings['game_version'],
                                                 cls.settings['game_subtitle'],
                                                 str(cls.settings['window_size']))
        pygame.display.set_caption(cls.settings['game_caption'])

    @classmethod
    def load_image(cls, img, colorkey = (255, 255, 255)):
        # todo: add data file support/data dir fallback
        i = False
        try:
            i = pygame.image.load(os.path.join(cls.dir_img, img)).convert()
            if colorkey is -1:
                colorkey = i.get_at((0, 0))
            i.set_colorkey(colorkey, pygame.RLEACCEL)
        except pygame.error as err:
            if cls.debug:
                print(err)
        return i

    @classmethod
    def init_input(cls, config=False):
        # gamebutton dict
        cls.pressed_keys = []
        cls.pressed_mousebuttons = []

        cls.num_joysticks = 0

        # maybe add some configuration sometime not sure tbh fam
        # axes: 0 = vert: 1 = horiz: 2 = trig: 3 = horiz2: 4 = vert2
        # butts: a b x y lb rb back start ls rs
        #       +   -
        #   -           -
        # -   +       -   +
        #   +           +
        cls.controllers = {

        }
        cls.input_data = {}
        cls.input_data['mouse'] = {
            'pos': (0, 0),
            'prev': (0, 0)
        }
        cls.input_data['axes'] = {
            'player1_move_horiz': {
                'type': 'digital',
                'pos': 'moveRight',
                'neg': 'moveLeft',
                'deadzone': 0.5,
                'value': 0
            },
            'player1_move_vert': {
                'type': 'digital',
                'pos': 'moveDown',
                'neg': 'moveUp',
                'deadzone': 0.5,
                'value': 0
            }
        }
        # todo: remappable keys/buttons
        cls.input_data['buttons'] = {
            'moveUp': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(2),
                'key': pygame.K_w,
            },
            'moveLeft': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(3),
                'key': pygame.K_a,
            },
            'moveDown': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(4),
                'key': pygame.K_s,
            },
            'moveRight': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(14),
                'key': pygame.K_d,
            },
            'fireUp': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(15),
                'key': pygame.K_UP,
            },
            'fireLeft': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(17),
                'key': pygame.K_LEFT,
            },
            'fireDown': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(18),
                'key': pygame.K_DOWN,
            },
            'fireRight': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(27),
                'key': pygame.K_RIGHT,
            },
            'menu': {
                'pressed': False,
                'held': False,
                'gpio': GPIOButton(0),
                'key': pygame.K_ESCAPE,
            },
        }

        cls.events_input = []
        for e in range(pygame.KEYDOWN, pygame.JOYBUTTONUP + 1):
            cls.events_input.append(e)

        pygame.joystick.init()
        cls.num_joysticks = pygame.joystick.get_count()
        for j in range(cls.num_joysticks):
            pygame.joystick.Joystick(j).init()
            cls.controllers[j] = {}

        cls.input_initialized = True

    @classmethod
    def update_input(cls, events):
        # process input events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key not in cls.pressed_keys:
                    cls.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in cls.pressed_keys:
                    cls.pressed_keys.remove(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button not in cls.pressed_mousebuttons:
                    cls.pressed_mousebuttons.append(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in cls.pressed_mousebuttons:
                    cls.pressed_mousebuttons.remove(event.button)
            elif event.type in range(pygame.JOYAXISMOTION, pygame.JOYBUTTONUP + 1):
                print(vars(event)) # todo: actually do something here
            elif event.type is pygame.MOUSEMOTION:
                cls.input_data['mouse']['prev'] = cls.input_data['mouse']['pos']
                cls.input_data['mouse']['pos'] = event.pos
                # print('{0}, {1}'.format(cls.mouse['pos'], cls.mouse['prev']))

        # set/clear held status
        # todo: rework buttons, mayhap as a separate class, to simplify and standardise
        for b, button in cls.input_data['buttons'].items():
            if button['gpio'].is_pressed or button['key'] in cls.pressed_keys:
                button['held'] = True
                if not button['pressed']:
                    button['pressed'] = True
                else:
                    button['pressed'] = False
            else:
                button['pressed'] = False
                button['held'] = False

        for axis in cls.input_data['axes'].values():
            if axis['type'] is 'digital':
                axis['value'] = 1 if cls.input_data['buttons'][axis['pos']]['held'] else 0
                axis['value'] = -1 if cls.input_data['buttons'][axis['neg']]['held'] else axis['value']
            flip = False
            if axis['value'] < 0:
                flip = True
                axis['value'] = -axis['value']

            axis['value'] = 0 if axis['value'] < axis['deadzone'] else 1 if axis['value'] > 1 else axis['value']
            axis['value'] = -axis['value'] if flip else axis['value']

    @classmethod
    def stick_info(cls, stick = False):
        r = [0, cls.num_joysticks]
        if stick is not False:
            r[0] = stick
            r[1] = stick + 1

        info = []
        for s in range(r[0], r[1]):
            if s < cls.num_joysticks:
                j = pygame.joystick.Joystick(s)
                info.append(dict(id=j.get_id(),
                        name=j.get_name(),
                        numaxes=j.get_numaxes(),
                        numballs=j.get_numballs(),
                        numbuttons=j.get_numbuttons(),
                        numhats=j.get_numhats()
                        ))
        return info


    @classmethod
    def update(cls):
        cls.update_input(pygame.event.get(cls.events_input))
        cls.object_manager.update(cls.input_data)

    @classmethod
    def draw(cls):
        cls.surface.fill((0, 10, 30))
        cls.object_manager.draw(cls.surface)
        pygame.display.update()

    @classmethod
    def add_sprite(cls, **kwargs):
        spr = False
        groups = False
        pos = (0,0)

        for arg, val in kwargs.items():
            if arg is 'spr':
                spr = val
            elif arg is 'groups':
                groups = val
            elif arg is 'pos':
                pos = val


