from monkeyislang import exec_file

def test_if(capfd):
    exec_file("examples/if.mi")
    out, _err = capfd.readouterr()
    assert out == "It's a 1 pieces o' eight\n"

def test_factorial(capfd):
    exec_file("examples/factorial.mi")
    out, _err = capfd.readouterr()
    assert out == "It's a 8 pieces o' eight\nIt's a 40320 pieces o' eight\n"

def test_closure(capfd):
    exec_file("examples/closure.mi")
    out, _err = capfd.readouterr()
    assert out == "It's a green 3 pieces o' eight\n"

def test_factorial(capfd):
    exec_file("examples/factorial.mi")
    out, _err = capfd.readouterr()
    assert out == "It's a 8 pieces o' eight\nIt's a 40320 pieces o' eight\n"

def test_chromatic(capfd):
    exec_file("examples/chromatic.mi")
    out, _err = capfd.readouterr()
    assert out == "I'm carrying 0 bottles of grog, green 1 pieces o' eight, blue 1 pieces o' eight, red red 0 pieces o' eight, green red 1 pieces o' eight, blue red 1 pieces o' eight.\n"
