class ChildTracker():

    def __init__(self):

        self.child = ""

    def update_child(self, child):

        self.child = child.attrib["id"]

    def get_last_child(self):

        return self.child
