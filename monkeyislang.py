import sys
from copy import copy
import argparse
import readline
import traceback

def look_at(direct_object, inventory):
    if hasattr(direct_object, 'look_at'):
        print(direct_object.look_at())
    else:
        print("It's a %s" % (description(direct_object),))

def description(item):
    if hasattr(item, 'description'):
        return item.description
    return item.name

def use(direct_object, indirect_object, inventory):
    if hasattr(direct_object, 'use'):
        result = direct_object.use(indirect_object, inventory)
        if result != NotImplemented:
            return result

    if hasattr(indirect_object, 'use'):
        result = indirect_object.use(direct_object, inventory)
        if result != NotImplemented:
            return result

    raise ValueError("Can't use %s with %s" % (direct_object.name, indirect_object.name))

def push(direct_object):
    pass

def unwrap(item):
    if hasattr(item, 'unwrap'):
        return item.unwrap()
    return item

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
        direct_object = ProgramBlock(command['direct_object'], inventory, reader)
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
    def __init__(self, name, inventory, reader):
        self.name = name
        self.inventory = inventory
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

    def call(self, callers_inventory, argument):
        # print("---> CALL: ", self.name, description(argument))
        new_inventory = self.inventory.create_child()

        if argument:
            callers_inventory.remove(argument)
            new_inventory.append(AliasingWrapper(copy(unwrap(argument)), 'mysterious object'))
            new_inventory.append(PiecesOEight())
            new_inventory.append(BottlesOGrog())
            new_inventory.append(Shovel())

        try:
            self.execute(new_inventory)
        except ReturnValue as return_value:
            return_value = return_value.args[0]

            return_value = unwrap(return_value)

            if hasattr(argument, 'replace'):
                argument.replace(return_value)
                return_value = argument

            # print("Returning: ", return_value, description(return_value), return_value.name)

            callers_inventory.append(return_value)
            # print("<--- Returning from", self.name, description(return_value.args[0]))

    def __repr__(self):
        return f'<ProgramBlock {self.name!r}>'

class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    @property
    def pieces_o_eight(self):
        return self.wrapped.pieces_o_eight

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
        self.color = color
        super().__init__(wrapped)

    @property
    def name(self):
        return f'{self.color} {self.wrapped.name}'

    @property
    def description(self):
        return f'{self.color} {description(self.wrapped)}'

    def __copy__(self):
        return type(self)(copy(self.wrapped), self.color)

    def __repr__(self):
        return f'<ColorWraper {self.color} {self.wrapped!r}>'

class AliasingWrapper(Wrapper):
    def __init__(self, wrapped, name):
        self.name = name
        self.wrapped = wrapped
        super().__init__(wrapped)

    @property
    def description(self):
        return '%s which appears to be %s' % (self.name, description(self.wrapped),)

    def __copy__(self):
        return type(self)(copy(self.wrapped), self.name)

class ChromaticTriplicator:
    name = 'chromatic triplicator'

    @staticmethod
    def use(other, inventory):
        inventory.remove(other)
        inventory.append(ColorWrapper(copy(other), 'red'))
        inventory.append(ColorWrapper(copy(other), 'green'))
        inventory.append(ColorWrapper(copy(other), 'blue'))

class PiecesOEight:
    name = "pieces o' eight"

    def __init__(self, count=1):
        self.count = count

    @property
    def pieces_o_eight(self):
        return self.count

    @property
    def description(self):
        return "%d %s" % (self.count, self.name)

    def use(self, other, inventory):
        if not hasattr(other, 'pieces_o_eight'):
            return NotImplemented

        self.count += other.pieces_o_eight
        if self.count <= 0:
            other.count = -self.count
            self.count = 0
        else:
            other.count = 0
        return None

class BottlesOGrog:
    name = "bottles o' grog"
    def __init__(self, count=1):
        self.count = count

    @property
    def pieces_o_eight(self):
        return -self.count

    @property
    def description(self):
        return "%d %s" % (self.count, self.name)

class DuplicatingContraption:
    name = 'duplicating contraption'

    def use(self, other, inventory):
        if hasattr(other, 'count'):
            other.count *= 2
        else:
            raise ValueError("The %s doesn't fit in the %s" % (other.name, self.name))

class RootBeer:
    name = 'root beer'

    @staticmethod
    def use(other, inventory):
        if not hasattr(other, 'color'):
            raise ValueError("I can't clean that with root beer.")

        inventory.remove(other)
        inventory.append(other.wrapped)


class Scales:
    name = 'scales'

    def __init__(self):
        self.truthy = False

    def use(self, other, inventory):
        if not hasattr(other, 'pieces_o_eight'):
            return NotImplemented

        self.truthy = other.pieces_o_eight != 0
        return None
        # print("Comparison: ", self.truthy, other.pieces_o_eight, description(other))

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
        if not hasattr(other, 'pieces_o_eight'):
            return NotImplemented
        other.count *= self.factor
        return None

class NLicatorCreator:
    name = 'n-licator creator'

    @staticmethod
    def use(other, inventory):
        if not hasattr(other, 'pieces_o_eight'):
            return NotImplemented

        inventory.append(MultiplyingContraption(other.pieces_o_eight))
        return None

class ReturnValue(Exception):
    pass

class Shovel:
    name = 'shovel'

    @staticmethod
    def use(other, inventory):
        raise ReturnValue(other)

class VendingMachine:
    name = 'vending machine'

    @staticmethod
    def use(other, inventory):
        if not hasattr(other, 'pieces_o_eight') or other.pieces_o_eight == 0:
            raise ValueError("Needs coins for the vending machine.")

        other.count -= 1

        try:
            grog = inventory["bottles o' grog"]
            grog.count += 1
        except KeyError:
            inventory.append(BottlesOGrog(1))

def default_inventory():
    scene = Inventory([
        ChromaticTriplicator(),
        DuplicatingContraption(),
        Scales(),
        DishonestShopkeeper(),
        NLicatorCreator(),
        RootBeer(),
        VendingMachine(),
    ])

    return Inventory([
        PiecesOEight(1),
        BottlesOGrog(1),
    ], parent=scene)

def program_reader(filehandle):
    for line in filehandle:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        yield parse_line(line)

def exec_file(filename):
    inventory = default_inventory()

    reader = program_reader(iter(open(filename)))

    for parsed in reader:
        # print(parsed)
        exec_command(parsed, inventory, reader)

def repl_reader():
    while True:
        try:
            yield input("mi> ")
        except EOFError:
            break

def repl():
    inventory = default_inventory()

    while True:
        reader = program_reader(repl_reader())

        try:
            for parsed in reader:
                # print(parsed)
                try:
                    exec_command(parsed, inventory, reader)
                except Exception:
                    print("Error executing: ", parsed)
                    traceback.print_exc()
                    continue
        except Exception:
            traceback.print_exc()
            continue
        else:
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="Source file to execute", nargs='?')
    args = parser.parse_args()
    if args.file:
        exec_file(args.file)
    else:
        repl()

if __name__ == '__main__':
    main()
