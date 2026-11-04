# Dataset source

The included `Breast_Cancer.csv` was recovered from the [SEER Breast Cancer Data record on Zenodo](https://zenodo.org/records/5120960), DOI [10.5281/zenodo.5120960](https://doi.org/10.5281/zenodo.5120960). The record describes a 4,024-patient extract from the November 2017 SEER update.

For this dashboard, the downloaded table was normalized to match the 16 fields used by `breast_cancer.ipynb`: the empty source column was removed; the combined grade field was split into `differentiate` and numeric `Grade`; and race and marital status values were shortened to the categories shown in the notebook. A local consistency check confirmed 4,024 rows, 3,408 `Alive` and 616 `Dead` records, one duplicate row, and no missing cells, matching the notebook's reported counts.
