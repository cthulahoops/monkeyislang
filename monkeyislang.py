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

def exec_command(command, inventory, reader):
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

        if self.parent:
            return self.parent[name]

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
        # print("Using block: ", self.name, description(other))
        if hasattr(other, 'truthy'):
            if other.truthy:
                self.execute(inventory)
        else:
            self.call(inventory, argument=other)

    def execute(self, inventory):
        # print("EXECUTE: ", self.name)
        reader = iter(self.commands)

        for command in reader:
            # print(command)
            exec_command(command, inventory, reader)

    def call(self, inventory, argument):
        # print("---> CALL: ", self.name, description(argument))
        new_inventory = inventory.create_child()

        if argument:
            inventory.remove(argument)
            new_inventory.append(AliasingWrapper(argument, 'mysterious object'))
            new_inventory.append(AliasingWrapper(self, 'this'))
            new_inventory.append(PiecesOfEight())
            new_inventory.append(BottlesOfGrog())
            new_inventory.append(Shovel())

        try:
            self.execute(new_inventory)
        except ReturnValue as return_value:
            return_value = return_value.args[0].unwrap()

            if hasattr(argument, 'replace'):
                argument.replace(return_value)
                return_value = argument

            inventory.append(return_value)
            # print("<--- Returning from", self.name, description(return_value.args[0]))

class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    @property
    def pieces_of_eight(self):
        return self.wrapped.pieces_of_eight

    def use(self, other, inventory):
        return self.wrapped.use(other, inventory)

    @property
    def count(self):
        return self.wrapped.count

    @count.setter
    def count(self, value):
        self.wrapped.count = value

    def unwrap(self):
        if hasattr(self.wrapped, 'unwrap'):
            return self.wrapped.unwrap()
        return self.wrapped

    def replace(self, replacement):
        if hasattr(self.wrapped, 'replace'):
            self.wrapped.replace(replacement)
        else:
            self.wrapped = replacement

class ColorWrapper(Wrapper):
    def __init__(self, wrapped, color):
        self.name = '%s %s' % (color, wrapped.name)
        self.color = color
        super().__init__(wrapped)

class AliasingWrapper(Wrapper):
    def __init__(self, wrapped, name):
        self.name = name
        self.wrapped = wrapped
        super().__init__(wrapped)

    @property
    def description(self):
        return '%s which appears to be %s' % (self.name, description(self.wrapped),)

class ChromaticTriplicator:
    name = 'chromatic triplicator'

    @staticmethod
    def use(other, inventory):
        inventory.remove(other)
        inventory.append(ColorWrapper(copy(other), 'red'))
        inventory.append(ColorWrapper(copy(other), 'green'))
        inventory.append(ColorWrapper(copy(other), 'blue'))

class PiecesOfEight:
    name = 'pieces of eight'
    def __init__(self, count=1):
        self.count = 1

    @property
    def pieces_of_eight(self):
        return self.count

    @property
    def description(self):
        return "%d %s" % (self.count, self.name)

    def use(self, other, inventory):
        if not hasattr(other, 'pieces_of_eight'):
            return NotImplemented

        self.count += other.pieces_of_eight
        if self.count <= 0:
            other.count = -self.count
            self.count = 0
        else:
            other.count = 0
        return None

class BottlesOfGrog:
    name = 'bottles of grog'
    def __init__(self, count=1):
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
        if not hasattr(other, 'pieces_of_eight'):
            return NotImplemented

        self.truthy = other.pieces_of_eight != 0
        return None
        # print("Comparison: ", self.truthy, other.pieces_of_eight, description(other))

    @property
    def description(self):
        return "scales(%r)" % (self.truthy,)

class DishonestShopkeeper:
    name = 'dishonest shopkeeper'

    @staticmethod
    def use(other, inventory):
        if not hasattr(other, 'truthy'):
            return NotImplemented

        other.truthy = not other.truthy
        return None

class MultiplyingContraption:
    name = 'n-licator'
    def __init__(self, factor):
        self.factor = factor

    def use(self, other, inventory):
        if not hasattr(other, 'pieces_of_eight'):
            return NotImplemented
        other.count *= self.factor
        return None

class NLicatorCreator:
    name = 'n-licator creator'

    @staticmethod
    def use(other, inventory):
        if not hasattr(other, 'pieces_of_eight'):
            return NotImplemented

        inventory.append(MultiplyingContraption(other.pieces_of_eight))
        return None

class ReturnValue(Exception):
    pass

class Shovel:
    name = 'shovel'

    @staticmethod
    def use(other, inventory):
        raise ReturnValue(other)

def default_inventory():
    scene = Inventory([
        ChromaticTriplicator(),
        DuplicatingContraption(),
        Scales(),
        DishonestShopkeeper(),
        NLicatorCreator(),
    ])

    return Inventory([
        PiecesOfEight(1),
        BottlesOfGrog(1),
    ], parent=scene)

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
        # print(parsed)
        exec_command(parsed, inventory, reader)
        # print()

if __name__ == '__main__':
    main()
