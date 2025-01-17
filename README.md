# BMRB Data Processing Tool

A Python-based tool for automating the extraction and processing of chemical shift and secondary structure data from the Biological Magnetic Resonance Bank (BMRB). This tool collects Averaged Shift Values (ASV) and secondary structure data, processes it, and saves the output as CSV files for further analysis.

## Features
- **Scrape BMRB IDs**: Automatically scrape BMRB IDs from a given search URL.
- **ASV Data Extraction**: Retrieve residue-wise chemical shift values (C, CA, CB) for each BMRB ID.
- **PDB Data Extraction**: Extract associated PDB IDs for secondary structure data.
- **Secondary Structure Annotation**: Annotate chemical shift data with secondary structure information (HELIX, SHEET, etc.).
- **CSV Output**: Save processed data as structured CSV files for analysis.

## Workflow
1. **Input**:
   - A search URL from the BMRB website.
   - The number of BMRB IDs to process (`n`).

2. **Process**:
   - Scrape BMRB IDs from the input URL.
   - Extract ASV data for each BMRB ID.
   - Scrape associated PDB IDs from the data library page.
   - Download and parse secondary structure data from PDB files.
   - Combine ASV data with secondary structure annotations.

3. **Output**:
   - `shift_data_<BMRB_ID>.csv`: Contains ASV data.
   - `final_data_<BMRB_ID>.csv`: Annotated ASV data with secondary structure details.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Raymond-Owen1-137/BMRB-Data-Processing-Tool.git
   cd BMRB-Data-Processing-Tool
Install the required Python dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Usage
Run the script by providing a search URL and the number of BMRB IDs to process:

bash
Copy
Edit
python main.py
Example
To process the first 2 BMRB IDs from the URL:

python
Copy
Edit
process_bmrb_data("https://bmrb.io/search/query_grid/?data_types[]=carbon_shifts&polymers[]=polypeptide(L)", 2)
Project Structure
bash
Copy
Edit
BMRB-Data-Processing-Tool/
├── README.md              # Project documentation
├── requirements.txt       # List of Python dependencies
├── main.py                # Main script
├── data/                  # Folder for output CSV files
│   ├── shift_data_<BMRB_ID>.csv
│   └── final_data_<BMRB_ID>.csv
Dependencies
requests: For HTTP requests.
beautifulsoup4: For HTML parsing.
pandas: For data manipulation and saving CSV files.
re: For regular expressions.
random: For selecting PDB IDs randomly.
Future Improvements
Add command-line interface (CLI) for better usability.
Optimize data processing using parallelism.
Improve error handling and logging.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements
Biological Magnetic Resonance Bank (BMRB) for providing the data.
European Bioinformatics Institute (EBI) for hosting PDB data.
