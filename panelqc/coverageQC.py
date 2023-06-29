#!/usr/bin/env python3

"""
Compute Coverage QC metrics
"""

import os
from pathlib import Path
from typing import Tuple
import pandas as pd
import rich_click as click
from rich.console import Console
from rich import print
from rich.panel import Panel
from rich.text import Text

console = Console()


def getSampleName(filename: str) -> str:
    """Generate sample names from the file name"""
    return os.path.basename(filename).split(".")[0]


def formatOutfiles(
        panelRegionSummaryDf: pd.DataFrame,
        sampleName: str, sampleSummary: dict, outdir: Path
) -> pd.DataFrame:
    """Format output files"""

    summaryDf = pd.DataFrame(sampleSummary, index=list(range(1))).round(2)

    if outdir is None:
        outdir = os.getcwd()
    else:
        os.makedirs(outdir, exist_ok=True)

    panelOfn = os.path.join(outdir, f"Panel_regionQC_{sampleName}.tsv")
    summaryOfn = os.path.join(outdir, f"Sample_summaryQC_{sampleName}.tsv")
    panelRegionSummaryDf.to_csv(panelOfn, sep="\t", index=False)
    summaryDf.to_csv(summaryOfn, sep="\t", index=False)
    return os.path.abspath(panelOfn), os.path.abspath(summaryOfn)


def computeSampleSummary(
        summaryPosDf: pd.DataFrame, countDf: pd.DataFrame, sampleName: str,
        outdir: Path, outSummaryCounts: bool = False
) -> dict:
    """Compute sample level coverage summary"""
    summaryPosCount = pd.merge(
        summaryPosDf, countDf, on=['Chr.Pos'], how='left'
    ).fillna(0)

    if outSummaryCounts:
        if outdir is None:
            outdir = os.getcwd()

        summaryCountFile = os.path.join(
            outdir, f"{sampleName}_summaryPosCounts.tsv"
        )

        summaryPosCount.to_csv(
            summaryCountFile, sep="\t", index=False
        )

        print("The coverage values at all the positions in the panel are saved"
              "in the following file:")
        print(f"{summaryCountFile}\n")

    sampleMean = round(summaryPosCount[sampleName].mean(), 2)
    sampleMedian = round(summaryPosCount[sampleName].median(), 2)
    sampleSd = round(summaryPosCount[sampleName].std(), 2)
    cut_2SD = sampleMean - 2 * sampleSd
    cut_1pt5SD = sampleMean - 1.5 * sampleSd
    cut_1SD = sampleMean - 1 * sampleSd
    quantile_20 = round(summaryPosCount[sampleName].quantile(0.2), 2)
    fold_80 = round(sampleMean/quantile_20, 2)
    uoc = round(
        (len(summaryPosCount[summaryPosCount[sampleName] > 0.2*sampleMean]) /
         len(summaryPosCount))*100, 2
    )
    cov = round(sampleSd/sampleMean, 2)

    return {
        'Sample': sampleName,
        'sampleMean': sampleMean,
        'sampleMedian': sampleMedian,
        'sampleSD': sampleSd,
        'CV': cov,
        'cut_2SD': cut_2SD,
        'cut_1pt5SD': cut_1pt5SD,
        'cut_1SD': cut_1SD,
        'quantile_20': quantile_20,
        'fold_80': fold_80,
        'uniformityOfCoverage': uoc
    }


def groupRegionStatsOverSampleSummary(
        group: pd.core.groupby.DataFrameGroupBy, sampleSummary: dict,
        sampleName: str
) -> pd.Series:
    """Compute region-wise group level statstics"""
    regionStatCols = ["basecount_2SD", "basecount_1.5SD", "basecount_1SD"]
    summaryStatCols = ["cut_2SD", "cut_1pt5SD", "cut_1SD"]
    statColsDict = dict(zip(summaryStatCols, regionStatCols))
    statList = []
    cols = []
    for cutoff in statColsDict:
        statList.append(
            group.loc[
                group[sampleName] > sampleSummary[cutoff], sampleName
            ].count()
        )
        cols.append(statColsDict[cutoff])
    return pd.Series(statList, index=cols).round(2)


def computeRegionStatsOverSampleSummary(
        panelRegionMeans: pd.DataFrame, panelPosCount: pd.DataFrame,
        sampleSummary: dict, sampleName: str
) -> Tuple[pd.DataFrame, dict]:
    """Compute number of bases per region having depth of coverage above
    specified sample level cut-offs in sampleSummary
    """
    groupCols = ["Chr", "Start", "End", "Gene", "RegionLength"]
    panelRegionStats = panelPosCount.drop(
        columns=['Chr.Pos']
    ).groupby(
        groupCols
    ).apply(
        groupRegionStatsOverSampleSummary, sampleSummary, sampleName
    ).reset_index()

    panelRegionStats = pd.merge(
        panelRegionMeans, panelRegionStats, on=groupCols, how='left'
    ).drop_duplicates().reset_index(drop=True)

    sampleSummary['Pcntbase_2SD'] = round(
        (panelRegionStats['basecount_2SD'].sum() /
         panelRegionStats['paddedLength'].sum())*100, 2
    )
    sampleSummary['Pcntbase_1.5SD'] = round(
        (panelRegionStats['basecount_1.5SD'].sum() /
         panelRegionStats['paddedLength'].sum())*100, 2
    )
    sampleSummary['Pcntbase_1SD'] = round(
        (panelRegionStats['basecount_1SD'].sum() /
         panelRegionStats['paddedLength'].sum())*100, 2
    )
    return (panelRegionStats, sampleSummary)


def computeRegionSummaries(
        padPosDf: pd.DataFrame, countDf: pd.DataFrame, sampleName: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute mean and SD of depth of coverage over bases in regions"""
    padPosCount = pd.merge(
        padPosDf, countDf, on=['Chr.Pos'], how='left'
    ).drop_duplicates().fillna(0).reset_index(drop=True)
    panelRegionMeans = padPosCount.groupby(
        ['Chr', 'Start', 'End', 'Gene', 'RegionLength']
    ).agg(
        paddedLength=(sampleName, 'count'),
        Mean=(sampleName, 'mean'),
        SD=(sampleName, 'std'),
    ).reset_index()
    return padPosCount, panelRegionMeans.round(2)


def processSampleCoverage(
        singleCountFilename: Path, padPosDf: pd.DataFrame,
        summaryPosDf: pd.DataFrame, outdir: Path, outSummaryCounts: bool
):
    """Process coverageQC for single count file"""
    countDf = pd.read_csv(
            singleCountFilename, sep="\t", index_col=None, header=0,
            names=[
                'Chr', 'Pos', 'A_Q_30', 'C_Q_30', 'G_Q_30', 'T_Q_30', 'N_Q_30'
            ],
            dtype={
                "Chr": "object", "Pos": "int64", "A_Q_30": "int64",
                "C_Q_30": "int64", "G_Q_30": "int64", "T_Q_30": "int64",
                "N_Q_30": "int64"
            },
            usecols=["Chr", "Pos", "N_Q_30"]
        )
    countDf['Chr.Pos'] = countDf['Chr'] + "." + countDf['Pos'].astype(str)
    countDf = countDf[["Chr.Pos", "N_Q_30"]]
    sampleName = getSampleName(singleCountFilename)
    countDf.rename(
        columns={'N_Q_30': sampleName},
        inplace=True
    )

    console.log(f"Loaded count file for {sampleName}")
    sampleSummary = computeSampleSummary(
        summaryPosDf, countDf, sampleName, outdir, outSummaryCounts
    )
    console.log(f"Computed sample summary for {sampleName}")
    panelPosCount, panelRegionMeans = computeRegionSummaries(
        padPosDf, countDf, sampleName
    )
    console.log(f"Computed region summaries for {sampleName}")
    regionSummaries, sampleSummary = \
        computeRegionStatsOverSampleSummary(
            panelRegionMeans, panelPosCount, sampleSummary, sampleName
        )

    panelOfn, summaryOfn = formatOutfiles(
        regionSummaries, sampleName, sampleSummary, outdir
    )
    console.log(f"CoverageQC processing completed for {sampleName}")
    panel = Panel(
        Text(
            f"Metrics for: {sampleName}\n" +
            "\nSample level statistics over coverage values - \n" +
            f"Mean: {sampleSummary['sampleMean']}\n" +
            f"Standard deviation: {sampleSummary['sampleSD']}\n\n" +
            f"Panel coverageQC file:\n{panelOfn}\n" +
            f"Sample summary file:\n{summaryOfn}\n",
            justify="left")
    )
    print()
    print(panel)
    return panelOfn, summaryOfn


def computeCoverage(
        panelPosFile: Path, summaryPosFile: Path, countFile: list[Path],
        outdir: Path, outSummaryCounts: bool
):
    """Compute coverage QC for given samples"""
    with console.status(
        "[bold green] Processing coverageQC...", spinner='bouncingBall'
    ):
        paddedPanelPositions = pd.read_csv(
            panelPosFile, sep="\t", index_col=None,
            dtype={
                "Chr.Pos": "object", "Chr": "object", "Start": "int64",
                "End": "int64", "Gene": "object", "RegionLength": "int64"
            }
        ).drop_duplicates()
        console.log("Loaded panel definition", log_locals=False)
        sampleSummaryPositions = pd.read_csv(
            summaryPosFile, sep="\t", dtype={"Chr.Pos": "object"},
            index_col=None
        ).drop_duplicates()
        console.log("Loaded sample summary positions", log_locals=False)

        for countfn in list(set(countFile)):
            console.log(f"Working on sample: {countfn}", log_locals=False)
            panelOfn, summaryOfn = processSampleCoverage(
                countfn, paddedPanelPositions, sampleSummaryPositions, outdir,
                outSummaryCounts
            )
    return panelOfn, summaryOfn


@click.command(
        name="coverageQC",
        help="Compute coverage across panel regions"
)
@click.option(
    "--panelPosFile", type=Path,
    help="File with panel positions as generated by buildIndex command."
    "File should have six columns: Chr.Pos, Chr, Start, End, Gene, "
    "RegionLength",
    required=True
)
@click.option(
    "--summaryPosFile", type=Path,
    help="File with unique positions in the panel to compute sample level"
    " summary statistics. File should have one column: "
    "Chr.Pos, as generated by buildIndex command. ",
    required=True
)
@click.option(
    "--countFile", type=Path, multiple=True,
    help="Count file(s) generated by SequencErr program. File(s) should've"
    " seven columns: Chr, Pos, A_Q_30, C_Q_30, G_Q_30, T_Q_30, N_Q_30",
    required=True
)
@click.option(
    "--outdir", type=Path, default=None,
    help="Output directory path. ",
    required=False
)
@click.option(
    "--outSummary/--no-outSummary", type=bool, default=False,
    help="Output counts at summary positions",
    required=False
)
def main(panelposfile, summaryposfile, countfile, outdir, outsummary):
    computeCoverage(
        panelPosFile=panelposfile,
        summaryPosFile=summaryposfile,
        countFile=countfile,
        outdir=outdir,
        outSummaryCounts=outsummary
    )


if __name__ == "__main__":
    main()
