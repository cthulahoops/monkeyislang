from monkeyislang import use, PiecesOfEight, BottlesOfGrog, Scales

def test_use_addition():
    direct = PiecesOfEight(5)
    indirect = PiecesOfEight(9)

    use(direct, indirect, None)

    assert direct.pieces_of_eight == 14
    assert indirect.pieces_of_eight == 0

def test_use_subtraction():
    direct = PiecesOfEight(9)
    indirect = BottlesOfGrog(4)

    use(direct, indirect, None)

    assert direct.pieces_of_eight == 5
    assert indirect.pieces_of_eight == 0

def test_use_subtraction_negative():
    direct = PiecesOfEight(9)
    indirect = BottlesOfGrog(15)

    use(direct, indirect, None)

    assert direct.pieces_of_eight == 0
    assert indirect.pieces_of_eight == -6

def test_scales():
    direct = PiecesOfEight(7)
    scales = Scales()

    use(direct, scales, None)

    assert scales.truthy
