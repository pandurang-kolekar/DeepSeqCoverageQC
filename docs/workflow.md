## Workflow

### Steps in the DeepSeqCoverageQC workflow

``` mermaid
graph TD
  A(panelFile) ----> B[/buildIndex/];
  B -- panelPosFile, summaryPosFile -->C[/computeCoverageQC/];
  D(BAM) ----> E[/SequencErr/];
  F(panelBedFile) ----> E[/SequencErr/];
  E -- countFile -->C;
  C --> G(Panel_regionQC)
  C --> H(Sample_summaryQC)

```
