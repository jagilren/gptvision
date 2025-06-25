import os
#Elimina Archivo que contenga Apostrofes
def delete_csvs_with_apostrophe(folder_path):
    """
    Deletes all .csv files in the given folder that contain a single quote (') character.
    """
    deleted_files = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "'" in content:
                        os.remove(file_path)
                        deleted_files.append(filename)
                        print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not deleted_files:
        print("No CSV files containing apostrophes were found.")
    else:
        print(f"\nDeleted {len(deleted_files)} file(s) containing apostrophes.")

# Example usage:
# delete_csvs_with_apostrophe("C:/your/folder/path")
