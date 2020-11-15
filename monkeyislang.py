import sys
from copy import copy

def look_at(direct_object, inventory):
    try:
        attr = direct_object.look_at
    except AttributeError:
        print("It's a %s" % (description(direct_object),))
    else:
        print(attr())

def description(item):
    try:
        return item.description
    except AttributeError:
        return item.name

def use(direct_object, indirect_object, inventory):
    try:
        attr = direct_object.use
    except AttributeError:
        pass
    else:
        result = attr(indirect_object, inventory)
        if result != NotImplemented:
            return result

    try:
        attr = indirect_object.use
    except AttributeError:
        raise ValueError("Can't use %s with %s" % (direct_object.name, indirect_object.name))

    return attr(direct_object, inventory)



def push(direct_object):
    pass


ACTIONS = {
    "open": None,
    "close": None,
    "push": None,
    "pull": None,
    "walk to": None,
    "pick up": None,
    "talk to": None,
    "give": None,
    "use": use,
    "look at": look_at,
    "turn on": None,
    "turn off": None,
}


PREPOSITIONS = {"give": "to", "use": "with"}

def parse_line(line):
    words = line.split()

    if words[0] in ACTIONS:
        action = words[0]
        words = words[1:]
    elif words[0] + ' ' + words[1] in ACTIONS:
        action = words[0] + ' ' + words[1]
        words = words[2:]
    else:
        raise ValueError("Invalid action %r" % (words))

    preposition = PREPOSITIONS.get(action)
    if preposition:
        preposition_position = words.index(preposition)
        direct_object = ' '.join(words[:preposition_position])
        indirect_object = ' '.join(words[preposition_position+1:])
    else:
        direct_object = ' '.join(words)
        indirect_object = None

    return {
        'action': action,
        'direct_object': direct_object,
        'indirect_object': indirect_object,
    }

def exec_command(command, inventory, location, reader):
    if command['action'] == 'open':
        direct_object = ProgramBlock(command['direct_object'], reader)
        inventory.append(direct_object)
        return

    action = ACTIONS[command['action']]

    direct_object = inventory[command['direct_object']]

    if command['indirect_object']:
        indirect_object = inventory[command['indirect_object']]
        action(direct_object, indirect_object=indirect_object, inventory=inventory)
    else:
        action(direct_object, inventory=inventory)

class Inventory(list):
    def __init__(self, values, parent=None):
        super().__init__(values)
        self.parent = parent

    def __getitem__(self, name):
        if name == 'inventory':
            return self
        for item in self:
            if item.name == name:
                return item
        raise KeyError("I can't see %r here" % (name,))

    def look_at(self):
        return "I'm carrying %s." % (', '.join(description(item) for item in self),)

    def create_child(self):
        return Inventory([], self)

class ProgramBlock:
    def __init__(self, name, reader):
        self.name = name
        self.commands = []
        for item in reader:
            if item['action'] == 'close' and item['direct_object'] == name:
                break
            self.commands.append(item)

    def use(self, other, inventory):
        try:
            if other.truthy:
                self.execute(inventory)
                return
        except AttributeError:
            pass

        self.execute(inventory, mysterious_object=other)

    def execute(self, inventory, mysterious_object=None):
        if mysterious_object:
            inventory = inventory.create_child()
            inventory.mysterious_object = mysterious_object

        for command in self.commands:
            print(command)
            exec_command(command, inventory, {}, None)

class ChromaticTriplicator:
    name = 'chromatic triplicator'

    @staticmethod
    def use(other, inventory):
        inventory.remove(other)
        red_other = copy(other)
        red_other.name = 'red %s' % (red_other.name,)
        inventory.append(red_other)

        green_other = copy(other)
        green_other.name = 'green %s' % (green_other.name,)
        inventory.append(green_other)

        blue_other = copy(other)
        blue_other.name = 'blue %s' % (blue_other.name,)
        inventory.append(blue_other)

class PiecesOfEight:
    name = 'pieces of eight'
    def __init__(self, count):
        self.count = 1

    @property
    def pieces_of_eight(self):
        return self.count

    @property
    def description(self):
        return "%d %s" % (self.count, self.name)

    def use(self, other, inventory):
        try:
            self.count += other.pieces_of_eight
        except AttributeError:
            return NotImplemented
        if self.count <= 0:
            other.count = -self.count
            self.count = 0
        else:
            other.count = 0


class BottlesOfGrog:
    name = 'bottles of grog'
    def __init__(self, count):
        self.count = 1

    @property
    def pieces_of_eight(self):
        return -self.count

    @property
    def description(self):
        return "%d %s" % (self.count, self.name)

class DuplicatingContraption:
    name = 'duplicating contraption'

    def use(self, other, inventory):
        try:
            other.count *= 2
        except AttributeError:
            raise ValueError("The %s doesn't fit in the %s" % (other.name, self.name))

class Scales:
    name = 'scales'

    def __init__(self):
        self.truthy = False

    def use(self, other, inventory):
        try:
            self.truthy = other.pieces_of_eight != 0
        except AttributeError:
            return NotImplemented

def default_inventory():
    return Inventory([
        PiecesOfEight(1),
        BottlesOfGrog(1),
        ChromaticTriplicator(),
        DuplicatingContraption(),
        Scales()
    ])

def program_reader(filehandle):
    while True:
        line = filehandle.readline()
        if not line:
            break
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        yield parse_line(line)

def main():
    inventory = default_inventory()

    reader = program_reader(sys.stdin)

    for parsed in reader:
        print(parsed)
        exec_command(parsed, inventory, {}, reader)
        print()

if __name__ == '__main__':
    main()
