# Easy Pivot Dashboard

A simple Python application that converts hierarchical category data from CSV or Excel files into a readable tree structure.

## Features

- Upload CSV or Excel files with category hierarchies
- Automatically generates a tree structure from the data
- Copy the formatted hierarchy to clipboard
- Download the hierarchy as a text file
- Simple and intuitive web interface using Streamlit

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bkydataconsulting/easy-pivot-dashboard.git
cd easy-pivot-dashboard
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Upload your CSV or Excel file with the following columns:
   - PARENT CATEGORY
   - MASTER CATEGORY
   - SUBCATEGORY 1
   - SUBCATEGORY 2

4. View the generated hierarchy and use the buttons to copy or download the result

## Requirements

- Python 3.9 or higher
- Dependencies listed in requirements.txt

## License

MIT License 