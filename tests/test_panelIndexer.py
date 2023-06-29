import deepseqcoverageqc.panelIndexer

"""
Basic Test cases
"""


def test_expandRegion():
    assert deepseqcoverageqc.panelIndexer.expandRegion(10, 10, 0) == [10]


def test_expandRegionWithPadding():
    assert deepseqcoverageqc.panelIndexer.expandRegion(10, 10, 1) == [9, 10, 11]
