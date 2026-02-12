import csv

CSV_FILE = "cell_mapping_template.csv"

def check_addresses():
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print(f"Header: {header}")
        
        count = 0
        non_empty = 0
        examples = []
        
        for row in reader:
            count += 1
            if len(row) > 4:
                addr = row[4].strip()
                if addr:
                    non_empty += 1
                    if len(examples) < 10:
                        examples.append(f"Row {count+1}: {row}")

    print(f"Total Rows: {count}")
    print(f"Rows with Non-Empty Address: {non_empty}")
    if examples:
        print("Examples:")
        for ex in examples:
            print(ex)

if __name__ == "__main__":
    check_addresses()
