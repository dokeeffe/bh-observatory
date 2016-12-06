
class FakeRoofSwitchInspector(object):
    def __init__(self, state):
        self.state = state
    def query(self):
        return self.state

class FakePowerController(object):
    def poweroff_equipment(self):
        pass
    def poweroff_pc(self):
        pass