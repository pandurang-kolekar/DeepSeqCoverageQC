#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Tuple
import pandas as pd
import rich_click as click
from rich.console import Console
from rich.progress import Progress

console = Console()


def getSampleName(filename: str) -> str:
    """Generate sample names from the file name"""
    return os.path.basename(filename).split(".")[0]


def formatNumbersInDataframe(df: pd.DataFrame, digits=2) -> pd.DataFrame:
    """Format float numbers in dataframe to given places of digits"""
    for col in df.columns:
        if df[col].dtypes == float:
            df[col] = [round(val, digits) for val in df[col]]
    return df


def formatOutfiles(
        panelRegionSummaryDf: pd.DataFrame,
        sampleName: str, sampleSummary: dict, outdir: Path
) -> pd.DataFrame:
    """Format output files"""

    summaryDf = formatNumbersInDataframe(
        pd.DataFrame(sampleSummary, index=list(range(1)))
    )

    if outdir is None:
        outdir = os.getcwd()
    else:
        os.makedirs(outdir, exist_ok=True)

    panelOfn = os.path.join(outdir, f"Panel_regionQC_{sampleName}.tsv")
    summaryOfn = os.path.join(outdir, f"Sample_summaryQC_{sampleName}.tsv")
    panelRegionSummaryDf.to_csv(panelOfn, sep="\t", index=False)
    summaryDf.to_csv(summaryOfn, sep="\t", index=False)
    return panelOfn, summaryOfn


def formatOutfiles_v2(
        reginMeansDf: pd.DataFrame, reginSummaryDf: pd.DataFrame,
        sampleName: str, sampleSummary: dict, outdir: Path
) -> pd.DataFrame:
    """Format output files"""
    panelRegionSummaryDf = formatNumbersInDataframe(
        pd.merge(
            reginMeansDf, reginSummaryDf, how='left',
            on=['Chr', 'Start', 'End', 'Gene', 'RegionLength']
        ).drop_duplicates().reset_index(drop=True)
    )

    summaryDf = formatNumbersInDataframe(
        pd.DataFrame(sampleSummary, index=list(range(1)))
    )

    if outdir is None:
        outdir = os.getcwd()
    else:
        os.makedirs(outdir, exist_ok=True)

    panelOfn = os.path.join(outdir, f"Panel_regionQC_{sampleName}.tsv")
    summaryOfn = os.path.join(outdir, f"Sample_summaryQC_{sampleName}.tsv")
    panelRegionSummaryDf.to_csv(panelOfn, sep="\t", index=False)
    summaryDf.to_csv(summaryOfn, sep="\t", index=False)
    return panelOfn, summaryOfn


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
    sampleSd = round(summaryPosCount[sampleName].std(), 2)
    cut_2SD = sampleMean - 2 * sampleSd
    cut_1pt5SD = sampleMean - 1.5 * sampleSd
    cut_1SD = sampleMean - 1 * sampleSd

    return {
        'Sample': sampleName,
        'sampleMean': sampleMean,
        'sampleSD': sampleSd,
        'cut_2SD': cut_2SD,
        'cut_1pt5SD': cut_1pt5SD,
        'cut_1SD': cut_1SD
    }


def groupRegionStatsOverSampleSummary(
        group: pd.core.groupby.DataFrameGroupBy, sampleSummary: dict,
        sampleName: str
) -> pd.Series:
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


def processSingleRegionDf_v2(
        chr: str, start: int, end: str, gene: str, padPosCount: pd.DataFrame,
        sampleSummary: dict
) -> Tuple[int, int, int]:
    """
    Compute number of bases in a region with coverage values above
    a. Mean(Sample level coverages) - 2* SD(Sample level coverages)
    b. Mean(Sample level coverages) - 1.5* SD(Sample level coverages)
    c. Mean(Sample level coverages) - 1* SD(Sample level coverages)
    """
    regionDf = padPosCount[
            (padPosCount['Chr'] == chr) &
            (padPosCount['Start'] == start) &
            (padPosCount['End'] == end)
        ]
    nRegion = len(regionDf)
    n_2SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_2SD']
    ])
    n_1pt5SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_1pt5SD']
    ])
    n_1SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_1SD']
    ])

    return [chr, start, end, nRegion, n_2SD, n_1pt5SD, n_1SD]


def computeRegionStatsOverSampleSummary_v2(
        padPosCount: pd.DataFrame, sampleSummary: dict
) -> list:
    """
    Compute number of bases in regions with coverage values above
    a. Mean(Sample level coverages) - 2* SD(Sample level coverages)
    b. Mean(Sample level coverages) - 1.5* SD(Sample level coverages)
    c. Mean(Sample level coverages) - 1* SD(Sample level coverages)
    """
    regions = padPosCount[['Chr', 'Start', 'End', 'Gene', 'RegionLength']]\
        .drop_duplicates()
    regionStats = [
        processSingleRegionDf_v2(
            row.Chr, row.Start, row.End, row.Gene, padPosCount, sampleSummary
        ) for row in regions.itertuples()
    ]

    regionStatsDf = pd.DataFrame(
        regionStats, columns=[
            'Chr', 'Start', 'End', 'paddedLength', 'basecount_2SD',
            'basecount_1.5SD', 'basecount_1SD'
        ]
    )

    sampleSummary['Pcntbase_2SD'] = round(
        (regionStatsDf['basecount_2SD'].sum() /
         regionStatsDf['paddedLength'].sum())*100, 2
    )
    sampleSummary['Pcntbase_1.5SD'] = round(
        (regionStatsDf['basecount_1.5SD'].sum() /
         regionStatsDf['paddedLength'].sum())*100, 2
    )
    sampleSummary['Pcntbase_1SD'] = round(
        (regionStatsDf['basecount_1SD'].sum() /
         regionStatsDf['paddedLength'].sum())*100, 2
    )

    return (pd.merge(
        regions, regionStatsDf, on=['Chr', 'Start', 'End'], how='left'
    ).drop_duplicates().reset_index(drop=True), sampleSummary)


def processSingleRegionDf_v1(
        regionDf: pd.DataFrame, sampleSummary: dict
) -> Tuple[int, int, int]:
    """
    Compute number of bases in a region with coverage values above
    a. Mean(Sample level coverages) - 2* SD(Sample level coverages)
    b. Mean(Sample level coverages) - 1.5* SD(Sample level coverages)
    c. Mean(Sample level coverages) - 1* SD(Sample level coverages)
    """

    nRegion = len(regionDf)
    n_2SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_2SD']
    ])
    n_1pt5SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_1pt5SD']
    ])
    n_1SD = len(regionDf[
        regionDf[regionDf.columns[-1]] > sampleSummary['cut_1SD']
    ])
    return nRegion, n_2SD, n_1pt5SD, n_1SD


def computeRegionStatsOverSampleSummary_v1(
        padPosCount: pd.DataFrame, sampleSummary: dict
) -> Tuple[pd.DataFrame, dict]:
    """
    Compute number of bases in regions with coverage values above
    a. Mean(Sample level coverages) - 2* SD(Sample level coverages)
    b. Mean(Sample level coverages) - 1.5* SD(Sample level coverages)
    c. Mean(Sample level coverages) - 1* SD(Sample level coverages)
    """
    regionTotalBases = []
    cut_2SD_val = []
    cut_1pt5SD_val = []
    cut_1SD_val = []

    regions = padPosCount[['Chr', 'Start', 'End', 'Gene', 'RegionLength']]\
        .drop_duplicates()

    for row in regions.itertuples():
        subdf = padPosCount[
            (padPosCount['Chr'] == row.Chr) &
            (padPosCount['Start'] == row.Start) &
            (padPosCount['End'] == row.End)
        ]

        nRegion, n_2SD, n_1pt5SD, n_1SD = processSingleRegionDf_v1(
            subdf, sampleSummary
        )
        regionTotalBases.append(nRegion)
        cut_2SD_val.append(n_2SD)
        cut_1pt5SD_val.append(n_1pt5SD)
        cut_1SD_val.append(n_1SD)

    sampleSummary['Pcntbase_2SD'] = round(
        (sum(cut_2SD_val)/sum(regionTotalBases))*100, 2
    )
    sampleSummary['Pcntbase_1.5SD'] = round(
        (sum(cut_1pt5SD_val)/sum(regionTotalBases))*100, 2
    )
    sampleSummary['Pcntbase_1SD'] = round(
        (sum(cut_1SD_val)/sum(regionTotalBases))*100, 2
    )

    return (pd.DataFrame({
        'Chr': regions['Chr'], 'Start': regions['Start'],
        'End': regions['End'], 'Gene': regions['Gene'],
        'RegionLength': regions['RegionLength'],
        'paddedLength': regionTotalBases,
        'basecount_2SD': cut_2SD_val, 'basecount_1.5SD': cut_1pt5SD_val,
        'basecount_1SD': cut_1SD_val
    }), sampleSummary)


def computeRegionSummaries(
        padPosDf: pd.DataFrame, countDf: pd.DataFrame, sampleName: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
    """Process single count file"""
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
    sampleSummary = computeSampleSummary(
        summaryPosDf, countDf, sampleName, outdir, outSummaryCounts
    )
    panelPosCount, panelRegionMeans = computeRegionSummaries(
        padPosDf, countDf, sampleName
    )

    regionSummaries, sampleSummary = \
        computeRegionStatsOverSampleSummary(
            panelRegionMeans, panelPosCount, sampleSummary, sampleName
        )

    panelOfn, summaryOfn = formatOutfiles(
        regionSummaries, sampleName, sampleSummary, outdir
    )

    print(
        f"\nProcessing sample: {sampleName}\n",
        "\nSample level statistics over coverage values - \n",
        f"Mean: {sampleSummary['sampleMean']}\n",
        f"Standard deviation: {sampleSummary['sampleSD']}\n",
        sep=""
    )

    return panelOfn, summaryOfn


def computeCoverage(
        panelPosFile: Path, summaryPosFile: Path, countFile: list[Path],
        outdir: Path, outSummaryCounts: bool
):
    count = 0
    nSamples = len(countFile)
    with Progress() as progress:
        task1 = progress.add_task(
            f"[red]Processing {nSamples} sample(s)", total=100
        )

    paddedPanelPositions = pd.read_csv(
        panelPosFile, sep="\t", index_col=None,
        dtype={
            "Chr.Pos": "object", "Chr": "object", "Start": "int64",
            "End": "int64", "Gene": "object", "RegionLength": "int64"
        }
    ).drop_duplicates()
    sampleSummaryPositions = pd.read_csv(
        summaryPosFile, sep="\t", dtype={"Chr.Pos": "object"},
        index_col=None
    ).drop_duplicates()
    with console.status(
        "[bold green] Processing coverageQC...", spinner='bouncingBall',
        refresh_per_second=2
    ):
        for countfn in list(set(countFile)):
            console.log(
                f"{countfn}"
            )
            panelOfn, summaryOfn = processSampleCoverage(
                countfn, paddedPanelPositions, sampleSummaryPositions, outdir,
                outSummaryCounts
            )
            print(f"Panel coverageQC file:\n{panelOfn}\n")
            print(f"Sample summary file:\n{summaryOfn}\n")
            count = count + 1
            fraction = round((count/nSamples)*100, 0)
            while not progress.finished:
                progress.update(task1, advance=fraction)
    return panelOfn, summaryOfn


@click.command(
        name="coverageQC",
        help="Compute coverage across panel regions"
)
@click.option(
    "--panelPosFile", type=Path,
    help="File with panel positions as generated by panelIndexer command."
    "File should have six columns: Chr.Pos, Chr, Start, End, Gene, "
    "RegionLength",
    required=True
)
@click.option(
    "--summaryPosFile", type=Path,
    help="File with unique positions in the panel to compute sample level"
    " summary statistics. File should have one column: "
    "Chr.Pos, as generated by panelIndexer command. ",
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
