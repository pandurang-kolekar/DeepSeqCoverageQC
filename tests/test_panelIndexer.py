import panelqc.panelIndexer

"""
Basic Test cases
"""


def test_expandRegion():
    assert panelqc.panelIndexer.expandRegion(10, 10, 0) == [10]


def test_expandRegionWithPadding():
    assert panelqc.panelIndexer.expandRegion(10, 10, 1) == [9, 10, 11]
