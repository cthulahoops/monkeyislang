import sys

ACTIONS = {
    "open": None,
    "close": None,
    "push": None,
    "pull": None,
    "walk to": None,
    "pick up": None,
    "talk to": None,
    "give": None,
    "use": None,
    "look at": None,
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

for line in sys.stdin:
    line = line.strip()
    if line.startswith('#') or not line:
        continue

    print(parse_line(line))

    print("<<<", line)
