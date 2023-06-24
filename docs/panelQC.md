# `panelQC`

Compute coverage QC for targeted deep sequencing data

**Usage**:

```console
$ panelQC [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `coverageQC`: Compute coverage across panel regions
* `panelIndexer`: Generate index for the panel

## `panelQC coverageQC`

Compute coverage across panel regions

**Usage**:

```console
$ panelQC coverageQC [OPTIONS] PANELPOSFILE SUMMARYPOSFILE SAMPLELIST
```

**Arguments**:

* `PANELPOSFILE`: [required]
* `SUMMARYPOSFILE`: [required]
* `SAMPLELIST`: [required]

**Options**:

* `--outsummarycounts / --no-outsummarycounts`: [default: no-outsummarycounts]
* `--help`: Show this message and exit.

## `panelQC panelIndexer`

Generate index for the panel

**Usage**:

```console
$ panelQC panelIndexer [OPTIONS] PANELFILE
```

**Arguments**:

* `PANELFILE`: [required]

**Options**:

* `--outfile PATH`
* `--padding INTEGER`: [default: 0]
* `--chrprefix / --no-chrprefix`: [default: no-chrprefix]
* `--help`: Show this message and exit.
