# Compute coverage QC metrics over regions in the panel

::: mkdocs-click
    :module: deeseqcoverageqc.panelQC
    :command: computeCoverageQC
    :depth: 0
    :list_subcommands: True
    :style: table

!!! note "How to generate count files?"

    The count files should be generated using SequencErr[^1]

    Please refer to [Generating count files](generateCounts.md)

## Output files

- **`computeCoverageQC`** generates two output files. 
  1. Panel_regionQC file
    - This file consists of the region level QC metrics for all the regions in the panel
  2. Sample_summaryQC file
    - - This file consists sample level QC metrics across all the positions in the panel

## Output format

### Panel_regionQC file

| Chr | Start | End | Gene | RegionLength | paddedLength | Mean | SD | basecount_2SD | basecount_1.5SD | basecount_1SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chr1 | 1718760 | 1718886 | GNB1 | 127 | 127 | 32883.11 | 3783.5 | 127 | 127 | 127 |
| chr1 | 1720482 | 1720718 | GNB1 | 237 | 237 | 30500.3 | 4670.12 | 237 | 237 | 237 |
| . | . | . | . | . | . | . | . | . | . | . |
| . | . | . | . | . | . | . | . | . | . | . |
| chrX | 153629033 | 153629205 | RPL10 | 173 | 173 | 17666.45 | 2345.65 | 173 | 173 | 166 |
| chrX | 153711341 | 153711341 | chrX.153711341.C.G | 1 | 1 | 25764.0 |  | 1 | 1 | 1 |

### Sample_summaryQC file

| Sample | sampleMean | sampleMedian | sampleSD | CV | cut_2SD | cut_1pt5SD | cut_1SD | quantile_20 | fold_80 | uniformityOfCoverage | Pcntbase_2SDPcntbase_1.5SD | Pcntbase_1SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-8_S5 | 21974.68 | 20209.0 | 14067.16 | 0.64 | -6159.64 | 873.94 | 7907.52 | 12573.0 | 1.75 | 94.92 | 100.0 | 98.37 | 90.87 |


[^1]: Davis, E.M., Sun, Y., Liu, Y., Kolekar, P. et al. SequencErr: measuring and suppressing sequencer errors in next-generation sequencing data. Genome Biol 22, 37 (2021). [https://doi.org/10.1186/s13059-020-02254-2](https://doi.org/10.1186/s13059-020-02254-2)