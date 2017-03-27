from qgissettingmanager import *

class MySettings(SettingManager):

    def __init__(self):
        SettingManager.__init__(self, 'TinglysningGml')

        self.add_setting(String('cvrnr', Scope.Global, ''))
        self.add_setting(String('organization', Scope.Global, ''))
        self.add_setting(String('output_path', Scope.Global, ''))
        self.add_setting(String('template_path', Scope.Global, ''))
