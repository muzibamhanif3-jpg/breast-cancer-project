https://github.com/muzibamhanif3-jpg/breast-cancer-project
# Breast Cancer Cohort Explorer

An interactive Streamlit dashboard based on the analyses in `breast_cancer.ipynb`.

## Setup

The project virtual environment is `.venv`. Activate it in PowerShell and install the app dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then start the dashboard:

```powershell
streamlit run app.py
```

## Data

`Breast_Cancer.csv` is included beside `app.py`. It contains the 4,024 records used by the notebook and is loaded automatically. The source copy is the SEER Breast Cancer dataset hosted by [Zenodo](https://zenodo.org/records/5120960). The source file had an empty column and combined differentiation and grade into one field; those were cleaned into the notebook's 16-column format. Race and marital status labels were shortened to match the notebook categories. You can also upload another CSV in the sidebar.

## Dashboard features

- Filters for age, recorded status, stage, race, receptor status, and tumor size.
- Cohort summary metrics and interactive charts for survival status, stage, tumor size, node involvement, age, recorded survival months, and numeric correlations.
- IQR outlier review, missing-value and duplicate counts, an interactive records table, and filtered CSV download.

The summaries are descriptive views of this historical dataset. They are not individual prognoses or medical advice.
