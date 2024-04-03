import os
import shutil
import time
import csv

# 1st part: Transfer EOD and transaction files
def process_files_part1():
    print("Processing files part 1...")
    # Define source and destination directories
    SOURCE_DIR = "OUTGOING_BUGS"
    DISC_DEST_DIR = "OUTGOING_DISC_0"
    TRN_DEST_DIR = "OUTGOING_TRN_0"

    # Ensure destination directories exist
    os.makedirs(DISC_DEST_DIR, exist_ok=True)
    os.makedirs(TRN_DEST_DIR, exist_ok=True)

    # Move files based on criteria
    for filename in os.listdir(SOURCE_DIR):
        print(f"Processing file: {filename}")
        source_path = os.path.join(SOURCE_DIR, filename)
        if "eod" in filename.lower():  # Check for "eod" or "EOD" in a case-insensitive manner
            dest_path = os.path.join(DISC_DEST_DIR, filename)
        else:
            dest_path = os.path.join(TRN_DEST_DIR, filename)
        shutil.move(source_path, dest_path)
    print("Processing files part 1 complete.")

# 2nd part: Transfer and fix NO_TRN
def process_files_part2():
    print("Processing files part 2...")
    source_dir = r'D:\OUTGOING_TRN_0'  
    destination_dir = r'D:\Ayala\tenant_api\storage\app\OUTGOING'  

    def count_transactions(content):
        # Split the content by newline to process each line separately
        lines = content.split('\n')
        count = 0
        transaction_started = False  # Flag to track if a transaction has started
        for line in lines:
            if line.strip().startswith('TRANSACTION_NO'):
                # If TRANSACTION_NO is found, start counting
                transaction_started = True
                if 'NO_TRN' not in line:
                    count += 1
            elif transaction_started:
                # If a transaction has started and we encounter a new line, check if it's the start of a new transaction
                if line.strip().startswith('TRANSACTION_NO'):
                    if 'NO_TRN' not in line:
                        count += 1
                else:
                    # If the line doesn't start with TRANSACTION_NO, it's part of the current transaction
                    continue
        return count

    def process_file(file_path):
        edited = False
        with open(file_path, 'r+') as file:
            content = file.read()
            if 'NO_TRN,0' in content:
                # If "NO_TRN,0" is found, replace "0" with the count of TRANSACTION_NO occurrences
                count = count_transactions(content)
                edited_content = content.replace('NO_TRN,0', f'NO_TRN,{count}')
                file.seek(0)  # Move the file pointer to the beginning
                file.write(edited_content)  # Write the edited content
                file.truncate()  # Truncate any remaining content
                edited = True
        return edited

    def move_file(source_path, destination_path):
        shutil.move(source_path, destination_path)

    def process_files():
        files_to_process = [
            file for file in os.listdir(source_dir)
            if file.endswith('.csv') or file.endswith('.txt')
        ]

        for file_name in files_to_process:
            source_file_path = os.path.join(source_dir, file_name)
            edited = process_file(source_file_path)
            if edited:
                destination_file_path = os.path.join(destination_dir, file_name)
                move_file(source_file_path, destination_file_path)
            else:
                move_file(source_file_path, os.path.join(destination_dir, file_name))
    print("Processing files part 2 complete.")
    
    # Process files in the source directory and fix NO_TRN
    process_files()

# 3rd part: Transfer and fix NO_DISC
def process_files_part3():
    print("Processing files part 3...")
    source_folder = 'D:/OUTGOING_DISC_0'
    destination_folder = 'D:/Ayala/tenant_api/storage/app/OUTGOING'

    def parse_line(line):
        parts = line.strip().split(',')
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        return '', ''

    def process_file(file_path):
        no_values = {'NO_SNRCIT': 0, 'NO_PWD': 0, 'NO_EMPLO': 0, 'NO_AYALA': 0, 'NO_STORE': 0, 'NO_OTHER_DISC': 0}
        no_disc_value = 0
        contains_no_disc = False

        if file_path.lower().endswith('.txt'):
            lines = []
            with open(file_path, 'r') as file:
                for line in file:
                    key, value = parse_line(line)
                    if key in no_values:
                        no_values[key] = int(value)
                    elif key == 'NO_DISC':
                        contains_no_disc = True
                        no_disc_value = int(value)
                    lines.append(line)

            if contains_no_disc:
                no_disc_value = sum(no_values.values())
                print(f"File {file_path} contains NO_DISC with value: {no_disc_value}")
                with open(file_path, 'w') as file:
                    for line in lines:
                        if line.startswith('NO_DISC'):
                            file.write(f'NO_DISC,{no_disc_value}\n')
                        else:
                            file.write(line)
                return True

        elif file_path.lower().endswith('.csv'):
            rows = []
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    key, value = parse_line(','.join(row))
                    if key in no_values:
                        no_values[key] = int(value)
                    elif key == 'NO_DISC':
                        contains_no_disc = True
                        no_disc_value = int(value)
                    rows.append(row)

            if contains_no_disc:
                no_disc_value = sum(no_values.values())
                print(f"File {file_path} contains NO_DISC with value: {no_disc_value}")
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for row in rows:
                        if row[0] == 'NO_DISC':
                            writer.writerow(['NO_DISC', no_disc_value])
                        else:
                            writer.writerow(row)
                return True

        return False

    def move_file(source_path, destination_path):
        try:
            shutil.move(source_path, destination_path)
            return True
        except Exception as e:
            print(f"Error moving file {source_path}: {e}")
            return False

    def process_and_move_file(file_path, destination_folder):
        edited = process_file(file_path)
        if edited:
            destination_path = os.path.join(destination_folder, os.path.basename(file_path))
            move_successful = move_file(file_path, destination_path)
            if move_successful:
                print(f"File {file_path} processed, edited, and moved successfully.")
            else:
                print(f"Error moving file {file_path}.")
        else:
            print(f"No changes made to file {file_path}.")

    # Process files in the source folder and fix NO_DISC
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)

        if os.path.exists(file_path):
            edited = process_file(file_path)
            if edited:
                print(f"File {file_path} processed and edited successfully.")
            else:
                print(f"No changes made to file {file_path}.")

            if os.path.exists(destination_folder):
                try:
                    shutil.move(file_path, destination_path)
                    print(f"File {file_path} moved to {destination_path} successfully.")
                except Exception as e:
                    print(f"Error moving file {file_path}: {e}")
            else:
                print(f"Destination folder {destination_folder} does not exist.")
        else:
            print(f"File {file_path} does not exist.")
    print("Processing files part 3 complete.")

# Main function to run all parts
def main():
    while True:
        process_files_part1()
        process_files_part2()
        process_files_part3()
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()
