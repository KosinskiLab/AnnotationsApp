import csv
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Open the input CSV file
        with open(input_file, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            
            # Get the field names from the input file
            fieldnames = reader.fieldnames
            
            # Create a DictWriter to print to stdout
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            
            # Iterate over each row in the input file
            for row in reader:
                #xiNET does not display annotations with commas correctly
                row['AnnotName'] = row['AnnotName'].replace(',', ';') 
                # if annotName starts with u, add a space, otherwise xiNET thinks its unicode code
                if row['AnnotName'].startswith('u'):
                    row['AnnotName'] = ' ' + row['AnnotName']
                # Write the updated row to stdout
                writer.writerow(row)
                
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

