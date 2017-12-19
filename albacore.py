from game import *


class Albacore(Game):
    error = False
    settings_file_name = 'settings'

    @classmethod
    def __init__(cls, **settings):
        super(Albacore, cls).__init__(**settings)

    @classmethod
    def run(cls):
        while not cls.quit:
            cls.update()
            if cls.input_data['buttons']['menu']['held']:
                cls.quit = True
            cls.draw()

        # shutdown
        cls.shutdown()

if __name__ == '__main__':
    try:
        pygame.init()
    except pygame.error as e:
        print(e)
    else:
        settings = {'game_name': 'albacore'}
        albacore = Albacore(**settings)
        info = albacore.stick_info()
        print('stick_info> num_joysticks: {0}'.format(albacore.num_joysticks))
        for stick in info:
            print('...........')
            for attrib in stick.keys():
                print("{0}: {1}".format(attrib, stick[attrib]))

        albacore.object_manager.add(albacore.load_image('link_test.png'))

        albacore.run()
