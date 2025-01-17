import requests  # Library to send HTTP requests
from bs4 import BeautifulSoup  # Library to parse HTML content
import pandas as pd  # Library to handle tabular data
import re  # Library for regular expressions
import random  # Library to select random values


def process_bmrb_data(search_url, n):
    """
    Process the first N BMRB IDs found on the given search URL and collect data.

    Parameters:
        search_url (str): URL of the BMRB search page.
        n (int): Number of BMRB IDs to process.

    Outputs:
        shift_data_<BMRB_ID>.csv: File containing ASV data.
        final_data_<BMRB_ID>.csv: File containing ASV data with secondary structure.
    """

    # Function to scrape BMRB IDs from the search page
    def scrape_bmrb_ids(search_url, n):
        """Scrape the first N BMRB IDs from the search page."""
        try:
            response = requests.get(search_url)  # Send GET request to the search URL
            response.raise_for_status()  # Raise exception if HTTP request fails
            soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML content

            bmrb_ids = []  # List to store BMRB IDs
            for link in soup.find_all("a", href=True):  # Loop through all links on the page
                href = link["href"]  # Get the href attribute of the link
                if "summary/index.php?bmrbId=" in href:  # Check if the link contains a BMRB ID
                    match = re.search(r"bmrbId=(\d+)", href)  # Extract the BMRB ID using regex
                    if match:
                        bmrb_ids.append(match.group(1))  # Add the BMRB ID to the list

            bmrb_ids = list(set(bmrb_ids))  # Remove duplicate IDs
            bmrb_ids = sorted(bmrb_ids, key=int)[:n]  # Sort IDs and limit to the first N
            print(f"Found BMRB IDs: {bmrb_ids}")  # Print the IDs for debugging
            return bmrb_ids  # Return the list of IDs
        except Exception as e:
            print(f"Error scraping BMRB IDs: {e}")  # Print error if something goes wrong
            return []  # Return an empty list if there is an error

    # Function to scrape ASV (chemical shift) data and save it to a CSV
    def scrape_ASV(url_directories, output_file):
        """Scrape ASV data and save to a CSV."""
        try:
            response = requests.get(url_directories)  # Send GET request to the ASV URL
            response.raise_for_status()  # Raise exception if HTTP request fails
            soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML content

            rows = []  # List to store ASV data rows
            current_residue = None  # Variable to store the current residue name

            for line in soup.get_text().splitlines():  # Loop through each line of the response text
                line = line.strip()  # Remove leading and trailing whitespace

                if line and "Overall:" in line:  # Check if the line contains residue information
                    parts = line.split("Overall:")  # Split the line to extract residue name
                    current_residue = parts[0].strip()  # Extract and store the residue name

                elif "Ave C Shift Values>>" in line:  # Check if the line contains chemical shift values
                    shift_data = line.split(">>")[1].strip()  # Extract the shift values
                    # Parse shift values into a dictionary
                    values = {key.strip(): val.strip() for key, val in (item.split("::") for item in shift_data.split("\t") if "::" in item)}
                    c_value = values.get("C", "None")  # Get the value for C
                    ca_value = values.get("CA", "None")  # Get the value for CA
                    cb_value = values.get("CB", "None")  # Get the value for CB

                    if current_residue:  # Ensure the residue name is available
                        rows.append([current_residue, c_value, ca_value, cb_value])  # Append the residue and shift values

            # Create a DataFrame from the rows
            df = pd.DataFrame(rows, columns=["Residue", "C", "CA", "CB"])
            df.to_csv(output_file, index=False)  # Save the DataFrame to a CSV file
            print(f"ASV data saved to {output_file}")  # Print success message
            return df  # Return the DataFrame
        except Exception as e:
            print(f"Error processing ASV data: {e}")  # Print error if something goes wrong
            return pd.DataFrame()  # Return an empty DataFrame if there is an error

    # Function to scrape secondary structure data for a given PDB ID
    def scrape_secondary_structure(pdb_id):
        """Scrape secondary structure data for a given PDB ID."""
        try:
            pdb_url = f"https://www.ebi.ac.uk/pdbe/entry-files/pdb{pdb_id.lower()}.ent"  # Construct the PDB file URL
            response = requests.get(pdb_url)  # Send GET request to fetch the PDB file
            response.raise_for_status()  # Raise exception if HTTP request fails

            secondary_structure = []  # List to store secondary structure lines
            for line in response.text.splitlines():  # Loop through each line of the PDB file
                if line.startswith("HELIX") or line.startswith("SHEET"):  # Check if the line contains HELIX or SHEET info
                    secondary_structure.append(line.strip())  # Add the line to the list

            return secondary_structure  # Return the list of secondary structure lines
        except Exception as e:
            print(f"Error fetching secondary structure for {pdb_id}: {e}")  # Print error if something goes wrong
            return []  # Return an empty list if there is an error

    # Function to scrape PDB IDs from the BMRB data library page
    def scrape_pdb_values(url_data_library):
        """Scrape PDB values from the data library page."""
        try:
            response = requests.get(url_data_library)  # Send GET request to the data library page
            response.raise_for_status()  # Raise exception if HTTP request fails
            soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML content

            pdb_values = []  # List to store PDB IDs
            for row in soup.find_all("tr"):  # Loop through all table rows on the page
                if "PDB" in row.get_text():  # Check if the row contains PDB information
                    pdb_cell = row.find_all("td")[-1]  # Get the last cell in the row
                    if pdb_cell:
                        raw_text = pdb_cell.get_text(" ", strip=True)  # Extract the text from the cell
                        pdb_values = re.findall(r"\b[A-Z0-9]{4}\b", raw_text)  # Extract PDB IDs using regex

            pdb_values = sorted(set(pdb_values))  # Remove duplicates and sort the PDB IDs
            pdb_values = [value for value in pdb_values if value != "RCSB"]  # Exclude invalid entries like "RCSB"
            return pdb_values  # Return the list of PDB IDs
        except Exception as e:
            print(f"Error scraping PDB values: {e}")  # Print error if something goes wrong
            return []  # Return an empty list if there is an error

    # Function to update ASV data with secondary structure information
    def update_data_with_structure(pdb_values, asv_df, bmrb_id):
        """Update the data table with secondary structure information."""
        try:
            random_pdb = random.choice(pdb_values)  # Randomly select a PDB ID
            print(f"Selected PDB ID: {random_pdb}")  # Print the selected PDB ID

            secondary_data = scrape_secondary_structure(random_pdb)  # Scrape secondary structure data for the PDB ID

            matched_data = []  # List to store parsed secondary structure information
            for line in secondary_data:  # Loop through each line of secondary structure data
                if line.startswith("HELIX"):  # Check if the line contains HELIX info
                    helix_start = int(line[21:25].strip())  # Extract the start position
                    helix_end = int(line[33:37].strip())  # Extract the end position
                    matched_data.append({"Type": "HELIX", "Start": helix_start, "End": helix_end})  # Add HELIX info
                elif line.startswith("SHEET"):  # Check if the line contains SHEET info
                    sheet_start = int(line[22:26].strip())  # Extract the start position
                    sheet_end = int(line[33:37].strip())  # Extract the end position
                    matched_data.append({"Type": "SHEET", "Start": sheet_start, "End": sheet_end})  # Add SHEET info

            structure_df = pd.DataFrame(matched_data)  # Create a DataFrame from the parsed data

            def match_residue(row):
                """Match each residue to its secondary structure."""
                residue_number = int(re.findall(r"\d+", row["Residue"])[0])  # Extract the residue number
                for _, struct_row in structure_df.iterrows():  # Loop through secondary structure DataFrame
                    if struct_row["Start"] <= residue_number <= struct_row["End"]:  # Check if residue falls in range
                        return struct_row["Type"]  # Return the secondary structure type
                return "None"  # Return "None" if no match is found

            asv_df["Secondary_Structure"] = asv_df.apply(match_residue, axis=1)  # Add secondary structure column
            final_output_file = f"final_data_{bmrb_id}.csv"  # Set the output file name
            asv_df.to_csv(final_output_file, index=False)  # Save the updated DataFrame to a CSV
            print(f"Updated data with secondary structure saved to {final_output_file}")  # Print success message

        except Exception as e:
            print(f"Error updating data with structure: {e}")  # Print error if something goes wrong

    # Main processing logic
    bmrb_ids = scrape_bmrb_ids(search_url, n)  # Scrape the BMRB IDs

    for bmrb_id in bmrb_ids:  # Loop through each BMRB ID
        # Construct URLs for ASV data and PDB information
        url_directories = f"https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr{bmrb_id}/validation/AVS_full.txt"
        url_data_library = f"https://bmrb.io/data_library/summary/index.php?bmrbId={bmrb_id}"

        # Scrape ASV data and PDB IDs
        asv_file = f"shift_data_{bmrb_id}.csv"
        asv_df = scrape_ASV(url_directories, asv_file)
        pdb_values = scrape_pdb_values(url_data_library)

        # Update ASV data with secondary structure information
        if not asv_df.empty and pdb_values:
            update_data_with_structure(pdb_values, asv_df, bmrb_id)


# Example usage
process_bmrb_data("https://bmrb.io/search/query_grid/?data_types%5B%5D=carbon_shifts&polymers%5B%5D=polypeptide%28L%29&polymer_join_type=OR", 2)
