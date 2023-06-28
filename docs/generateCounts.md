## Generate count files from the BAM files

!!! note "How to generate count files?"

    The count files should be generated using SequencErr[^1]

- Users are recommended to use `-regions` option to provide panel BED file to 
  restrict the counts to positions in the panel

```
$ sequencerr_2.09

Usage: sequencerr_2.09 [OPTION...] bam outfile

REQUIRED:
 bam                      Bamfile input, sorted by CHROM then START. A bam index must be present in the CWD.
 outfile                  Output file names to hold the base counts per coordinate.

OPTIONS:
-STDOUT=chr:start-end     Standard output for a specific region, no saved file needed.
-prefix=Chr/chr           Add prefix <text> to first column.
-regions=file.bed         Bed file of regions to report. Lines don't need to be sorted by chromosomes,
                          but coordinates within a chromosome must be sorted by START, END.
                             Reference names must match what's in the bamfile header.

 -chr=str1,str2...        Only report counts on the chromosomes listed. Names must be comma seperated and must match the reference names in the bam header.
 -trimLen=int             Number of bases to trim off the 5' and 3' of the read. Default is 5.
 -qCutHard=int            A hard threshold for discarding reads. If the fraction of bases with quality scores
                          falling below this value exceeds fcut, the read will be filtered.
 -fcut=double             Fraction of bases with a quality score less than <qCutHard> to tolerate. Default is 0.05
 -mincov=int              Minimum coverage required at a given position in order for the position to be reported. Default is 10.
 -qcut=int1               Report the number of bases that passes this quality threshold. Default is 30.
 -peRate=double           Fraction of errant base calls per tile to tolerate. Default is 0.0001.
 -pe=str                  Paired-error rate filename. If provided, the paired error rates will be reported.
 -bad=str                 A file of tile names to exclude from the analysis. The file should be line delimited
                          and fields should be ':' separated. This is the same format as what is returned
                          in the Paired-error rate file.
                          Example: Instrument:Flowcell:Lane:Tile

 -nodesize=int            Size of counter memory block allocation in base pairs. Larger is better for WGS, smaller is better for sparse data
                          such as that found in amplicon or whole exome sequencing. Default is 4096
 -minmapq=int             Sets a minimum MAPQ threshold that must be exceeded by a read's MAPQ in order to be counted. Default is 55

Citations:

     1. Davis, E.M., Sun, Y., Liu, Y. et al. SequencErr: measuring and suppressing sequencer errors in next-generation sequencing data.
     Genome Biol 22, 37 (2021). https://doi.org/10.1186/s13059-020-02254-2

     2. Ma, X., Shao, Y., Tian, L. et al. Analysis of error profiles in deep next-generation sequencing data.
     Genome Biol 20, 50 (2019). https://doi.org/10.1186/s13059-019-1659-6

LICENSE

A patent application has been filed based on the research disclosed in this software and related manuscript; the pending
patent does not restrict the research use although the commercial sale and use of this software are not permitted.

Copyright 2021 St. Jude Children's Research Hospital

Licensed under a modified version of the Apache License, Version 2.0 (the "License") for academic research use only; you
may not use this file except in compliance with the License. To inquire about commercial use, please contact the St. Jude
Office of Technology Licensing at scott.elmer@stjude.org.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
```


[^1]: Davis, E.M., Sun, Y., Liu, Y., Kolekar, P. et al. SequencErr: measuring and suppressing sequencer errors in next-generation sequencing data. Genome Biol 22, 37 (2021). [https://doi.org/10.1186/s13059-020-02254-2](https://doi.org/10.1186/s13059-020-02254-2)