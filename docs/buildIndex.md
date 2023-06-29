## Buid index

### Generate index for the panel

```
DeepSeqCoverageQC buildIndex --help
```

::: mkdocs-click
    :module: panelqc.panelQC
    :command: buildIndex
    :depth: 0
    :style: table

## Input file format for `--panelFile`

| Chr | Start | End | Gene |
| --- | --- | --- | --- |
| chr1 | 998582 | 998582 | chr1.998582.G.C |
| chr1 | 1098421 | 1098421 | chr1.1098421.C.T |
| chr1 | 1646371 | 1646371 | chr1.1646371.G.T |
| chr1 | 1718760 | 1718886 | GNB1 |
| chr1 | 1720482 | 1720718 | GNB1 |

## Output files

- **`buildIndex`** generates two output files. 
  1. `*_regions.txt` file
    - This file consists of expanded panel region positions retaining gene and length information
    - This file is used to calculate region level QC metrics using `computeCoverageQC`
  2. `*_uniquePositions.txt` file
    - This file consists of unique positions in the panel to calculate sample level QC metrics using `computeCoverageQC`

## Output format

###  `*_regions.txt` file (partial output)

!!! Note
    Please note that original region chr1:1718760-1718886 is being expanded
    over individual positions as shown under Chr.Pos column

| Chr.Pos | Chr | Start | End | Gene | RegionLength |
| --- | --- | --- | --- | --- | --- |
| chr1.1718760 | chr1 | 1718760 | 1718886 | GNB1 | 127 |
| chr1.1718761 | chr1 | 1718760 | 1718886 | GNB1 | 127 |
| chr1.1718762 | chr1 | 1718760 | 1718886 | GNB1 | 127 |
| chr1.1718763 | chr1 | 1718760 | 1718886 | GNB1 | 127 |

### `*_uniquePositions.txt` file (partial output)

| Chr.Pos |
| --- |
| chr1.100345409 |
| chr1.100939777 |
| chr1.101106981 |
| chr1.101750747 |
| chr1.102322817 |