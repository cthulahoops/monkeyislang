from monkeyislang import use, PiecesOEight, BottlesOGrog, Scales

def test_use_addition():
    direct = PiecesOEight(5)
    indirect = PiecesOEight(9)

    use(direct, indirect, None)

    assert direct.pieces_o_eight == 14
    assert indirect.pieces_o_eight == 0

def test_use_subtraction():
    direct = PiecesOEight(9)
    indirect = BottlesOGrog(4)

    use(direct, indirect, None)

    assert direct.pieces_o_eight == 5
    assert indirect.pieces_o_eight == 0

def test_use_subtraction_negative():
    direct = PiecesOEight(9)
    indirect = BottlesOGrog(15)

    use(direct, indirect, None)

    assert direct.pieces_o_eight == 0
    assert indirect.pieces_o_eight == -6

def test_scales():
    direct = PiecesOEight(7)
    scales = Scales()

    use(direct, scales, None)

    assert scales.truthy
