#!/usr/bin/env python3

"""
Generate index for the panel
"""

import os
import errno
from pathlib import Path
import pandas as pd
import rich_click as click


def expandRegion(start: int, end: int, padding: int) -> list:
    """
    Expand a region with padding
    """
    return list(range(start - padding, end + padding + 1))


def getExpandedRegions(panelRegions: pd.DataFrame, padding: int) \
        -> pd.DataFrame:
    """
    Expand all the regions in the panel considering padding
    """
    panelRegions['Pos'] = [
        expandRegion(start, end, padding) for start, end in
        zip(panelRegions['Start'], panelRegions['End'])
    ]
    return panelRegions.explode(
        'Pos', ignore_index=True
    ).sort_values(by=['Chr', 'Pos']).reset_index(drop=True)


def formatOutput(expandedRegions: pd.DataFrame, chrPrefix: bool) -> list:
    """
    Format output for the panel index and unique positions
    """
    if chrPrefix:
        expandedRegions['Chr'] = 'chr' + expandedRegions['Chr']
    expandedRegions['Chr.Pos'] = (
        expandedRegions['Chr'] + "." + expandedRegions['Pos'].astype('str')
    )

    expandedRegions['RegionLength'] = (
        expandedRegions['End'] - expandedRegions['Start'] + 1
    )
    returnCols = ['Chr.Pos', 'Chr', 'Start', 'End', 'Gene', 'RegionLength']
    cpos = expandedRegions[["Chr.Pos"]].drop_duplicates(
    ).reset_index(drop=True)
    return [expandedRegions[returnCols], cpos]


def buildPanelIndex(
        panelFile: Path, outfile: Path, padding: int = 0,
        chrPrefix: bool = False,
) -> list:
    """
    Build panel index over all the positions covered by regions in the panel,
    including padding on either sides.
    """

    if not panelFile.is_file():
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            panelFile
        )

    panelRegions = pd.read_csv(
        panelFile, sep="\t", usecols=['Chr', 'Start', 'End', 'Gene'],
        dtype={
            "Chr": "object", "Start": "int", "End": "int",
            "Gene": "object", "RegionLength": "int"
        }
    ).drop_duplicates()
    panelIndex = getExpandedRegions(panelRegions, padding)
    if outfile is None:
        outfile = (
            f'{os.getcwd()}/' + os.path.basename(panelFile)
        ) + f"_index_padding_{padding}.tsv"

    outFields = formatOutput(panelIndex, chrPrefix)
    outFields[0].to_csv(outfile, sep="\t", index=False)
    outFields[1].to_csv(f"{str(outfile)}_uniqPositions.txt",
                        sep="\t", index=False)

    print("\nPanel index is saved in the following file:")
    print(os.path.realpath(outfile), "\n")
    print("Unique positions in the panel are saved in the following file:")
    print(os.path.realpath(f"{str(outfile)}_uniqPositions.tsv"), "\n")

    return outFields


@click.command(
        name="panelIndexer",
        help="Build index for the panel"
)
@click.option(
    "--panelFile", type=click.Path(),
    help="File with panel regions. "
    "File should have four tab-delimited columns: Chr, Start, End, Gene",
    required=True
)
@click.option(
    "--outfile", type=click.Path(), default=None,
    help="Output file name. ",
    required=False
)
@click.option(
    "--padding", type=int, default=0,
    help="Padding (bp) for regions. ",
    required=False
)
@click.option(
    "--chr/--no-chr", type=bool, default=False,
    help="Add 'chr' prefix",
    required=False
)
def main(panelfile, outfile, padding, chr) -> list:
    buildPanelIndex(
        panelFile=panelfile,
        outfile=outfile,
        padding=padding,
        chrPrefix=chr
    )


if __name__ == "__main__":
    main()
