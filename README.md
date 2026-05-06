# FH Technikum Wien - Winter Tourism Data Analysis

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Pandas](https://img.shields.io/badge/pandas-%5E2.0-lightgrey?logo=pandas)
![Plotly](https://img.shields.io/badge/plotly-%5E5.0-lightgrey?logo=plotly)
![Dash](https://img.shields.io/badge/dash-%5E3.0-lightgrey?logo=dash)
![License](https://img.shields.io/badge/license-BSD%203--Clause-blue?logo=opensourceinitiative)
![GitHub](https://img.shields.io/badge/github-imosudi%2Fdata_analysis-black?logo=github)

A Dash dashboard for analysing Austrian tourism overnight stays from the Statistics Austria OGD dataset (2015-2024). The dashboard highlights winter vs summer performance, regional results, annual trends and top source markets.

## Getting Started

### macOS / Linux

```bash
git clone https://github.com/imosudi/data_analysis.git
cd data_analysis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows (PowerShell)

```powershell
git clone https://github.com/imosudi/data_analysis.git
cd data_analysis
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open the app in your browser at `http://127.0.0.1:8050`.

## Project Structure

```text
data_analysis/
├── app.py
├── assets
│   └── fhtw-logo.png
├── LICENSE
├── README.md
├── requirements.txt
└── dataset
    ├── 0-OGD_touextsai_Tour_HKL_1_HEADER.csv
    ├── 1-OGD_touextsai_Tour_HKL_1_C-SDB_TIT-0.csv
    ├── 2-OGD_touextsai_Tour_HKL_1_C-C93-2.csv
    ├── 3-OGD_touextsai_Tour_HKL_1_C-W96-0.csv
    ├── 4-OGD_touextsai_Tour_HKL_1.csv
    └── file_report.csv
```

3 directories, 11 files


## License

This project is licensed under the **GPL-3.0 license** - see the [LICENSE](./LICENSE) file for details.

## Author

**Mosudi Isiaka O.**  
📧 [mosudi.isiaka@gmail.com](mailto:mosudi.isiaka@gmail.com)  
💻 [https://github.com/imosudi](https://github.com/imosudi)


