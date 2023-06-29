<p align="center">

  <h1 align="center">
    DeepSeqCoverageQC
  </h1>
  <h3 align="center">
    Compute coverage QC metrics for deep targeted sequencing data
  </h3>

  <br>
  <p align="center">
   <a href="https://github.com/pandurang-kolekar/panelQC" target="_blank">
     <img alt="Status"
          src="https://img.shields.io/badge/status-active-success.svg" />
   </a>
   <a href="https://github.com/pandurang-kolekar/panelQC/issues" target="_blank">
     <img alt="Github Issues"
          src="https://img.shields.io/github/issues/stjudecloud/bioinformatics-tool-template"  />
   </a>
   <a href="https://github.com/pandurang-kolekar/panelQC/pulls"  target="_blank">
     <img alt="Pull Requests"
          src="https://img.shields.io/github/issues-pr/stjudecloud/bioinformatics-tool-template"  />
   </a>
   <a href="https://github.com/pandurang-kolekar/panelQC/blob/main/LICENSE" target="_blank">
     <img alt="License: Apache License 2.0"
          src="https://img.shields.io/badge/License-Apache2.0-blue.svg" />
   </a>
</p>

  <p align="center">
   <br/>
   <a href="#"><strong>Explore the docs »</strong></a>
   <br />
   <a href="#"><strong>Read the paper »</strong></a>
   <br />
   <br />
   <a href="https://github.com/pandurang-kolekar/panelQC/issues/new?assignees=&labels=&template=feature_request.md&title=Descriptive%20Title&labels=enhancement">Request Feature</a>
    | 
   <a href="https://github.com/pandurang-kolekar/panelQC/issues/new?assignees=&labels=&template=bug_report.md&title=Descriptive%20Title&labels=bug">Report Bug</a>
   <br />
    ⭐ Consider starring the repo! ⭐
   <br />
  </p>
</p>

---
## Quick Start

### Using [Miniconda](https://docs.conda.io/en/latest/miniconda.html)


```
conda create --name panelQC python==3.9
conda activate panelQC
python -m pip install git+https://github.com/pandurang-kolekar/panelQC.git@main
DeepSeqCoverageQC --help
```

### Using Pip
> **Note**
>   Requires [Python](https://www.python.org/) version >=3.9
    
```
python -m pip install git+https://github.com/pandurang-kolekar/panelQC.git@main
```
## Usage

`DeepSeqCoverageQC` is a command line interface (CLI) app with the following commands

```bash
$ DeepSeqCoverageQC --help

Usage: DeepSeqCoverageQC [OPTIONS] COMMAND [ARGS]...                                
                                                                                     
 Compute coverageQC for targeted deep sequencing data                                
                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                           │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────╮
│ buildIndex             Generate index for the panel                               │
│ computeCoverageQC      Compute coverageQC metrics across panel regions.           │
╰───────────────────────────────────────────────────────────────────────────────────╯

```

### Build panel index

```bash

$ DeepSeqCoverageQC buildIndex --help

Generate index for the panel                                                        
                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ *  --panelFile       PATH     File with panel regions. File should have four      │
│                               tab-delimited columns: Chr, Start, End, Gene        │
│                               [required]                                          │
│    --outfile         PATH     Output file name.                                   │
│    --padding         INTEGER  Padding (bp) for regions.                           │
│    --chr/--no-chr             Add 'chr' prefix                                    │
│    --help                     Show this message and exit.                         │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

### Compute region and sample level QC metrics

```bash

$ DeepSeqCoverageQC computeCoverageQC --help

Usage: DeepSeqCoverageQC computeCoverageQC [OPTIONS]                                
                                                                                     
 Compute coverageQC metrics across panel regions.                                    
                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│ *  --panelPosFile                  PATH  File with panel positions as generated   │
│                                          by buildIndex command.File should have   │
│                                          six columns: Chr.Pos, Chr, Start, End,   │
│                                          Gene, RegionLength                       │
│                                          [required]                               │
│ *  --summaryPosFile                PATH  File with unique positions in the panel  │
│                                          to compute sample level summary          │
│                                          statistics. File should have one column: │
│                                          Chr.Pos, as generated by buildIndex      │
│                                          command.                                 │
│                                          [required]                               │
│ *  --countFile                     PATH  Count file(s) generated by SequencErr    │
│                                          program. File(s) should've seven         │
│                                          columns: Chr, Pos, A_Q_30, C_Q_30,       │
│                                          G_Q_30, T_Q_30, N_Q_30                   │
│                                          [required]                               │
│    --outdir                        PATH  Output directory path.                   │
│    --outSummary/--no-outSummary          Output counts at summary positions       │
│    --help                                Show this message and exit.              │
╰───────────────────────────────────────────────────────────────────────────────────╯

```

## Publication

Manuscript under preparation

## Contact

- [Pandurang Kolekar](mailto:pandurang.kolekar@gmail.com)

## COPYRIGHT

Copyright © 2023 Pandurang Kolekar, St. Jude Children's Research Hospital