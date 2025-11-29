from pathlib import Path
import logging
import shutil
import os 
import json
import hashlib
from halo import Halo
from colorama import Fore, Style, init

init(autoreset=True)

DRY_RUN = False # Set to False to perform actual move

# -------- LOGGING SETUP --------
logging.basicConfig(filename= "log.txt",level=logging.INFO)

#-----------Print Banner-----------
print (Fore.CYAN + """
====================================
      FILE ORGANIZER SCRIPT""")

#---------Duplicate record ---------
Hash_Index_file = "hash_index.json"

def load_hash_index():
    if Path(Hash_Index_file).exists():
        try:
            return json.loads(Path(Hash_Index_file).read_text(encoding = 'utf-8'))
        except Exception:
            return {}
    return {}
    
def save_hash_index(index):
    Path(Hash_Index_file).write_text(json.dumps(index), encoding = 'utf-8')

def file_hash(path , chunk_size=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


#----------FUNCTION TO HANDLE DUPLICATE FILE NAMES--------
def get_unique_name(path):
    counter = 1
    while path.exists():
        new_name = f"{path.stem}_{counter}{path.suffix}"
        path = path.parent / new_name
        counter += 1
    return path



# -------- MAIN FUNCTION --------
def organizer_file(input_folder, output_folder):
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    #------------counter-----------
    total_file = 0
    moved_files = 0
    failed_files = 0
    duplicates_skipped = 0     # <---- FIXED BUG HERE
    total_size = 0

    logging.info("Starting file organization")

    hash_index = load_hash_index()
    if hash_index is None:
        hash_index = {}

    #-------- Check if input folder exists --------
    if not input_path.exists():
        raise FileNotFoundError(f"Input Folder doesn't exist: {input_path}")

    #----------- Create output folder if not exists -----------
    output_path.mkdir(exist_ok=True)

    categories = {
        "images": [".jpg", ".jpeg", ".png", ".gif"],
        "documents": [".pdf", ".txt", ".csv", ".docs"],
        "video": [".mp4", ".mov"],
        "audio": [".mp3", ".wav"]
    }

    #--------- Load existing hash index --------
    for cat in list(categories.keys()) + ["misc"]:
        if cat not in hash_index:
            hash_index[cat] = {}

     # -------- LOOP THROUGH FILES --------
    for file in input_path.iterdir():
        if file.is_file():
            total_file += 1

            #------calculate the file size ----------
            file_size = file.stat().st_size
            total_size += file_size
            file_extension = file.suffix.lower()

            category = None
            for cat, ext_list in categories.items():
                if file_extension in ext_list:
                    category = cat
                    break

            if category is None:
                category = "misc"

            # ---- Create category folder ----
            category_folder = output_path / category
            category_folder.mkdir(exist_ok=True)

            #----- compute content hash to detect duplicate ------
            try:
                h = file_hash(file)
            except Exception as e:
                failed_files +=1
                logging.error(f"Could not hash file {file.name}:{e}")
                continue

            #check if hash exists in the category
            if h in hash_index.get(category, {}):
                duplicates_skipped += 1
                existing_ref = hash_index[category][h]
                logging.info(f"Duplicate content detected. Skipping {file.name} (same as {existing_ref})")
                continue

            # ---- Handle duplicate file names ----
            destination = category_folder / file.name
            destination = get_unique_name(destination)

            if DRY_RUN:
                print(f"[DRY RUN] Would move file {file.name} to {destination}/")
                moved_files += 1
                logging.info(f"[DRY RUN] Would move file {file.name} to {destination}/")
            
            else:
                try:
                    shutil.move(str(file), str(destination))
                    moved_files += 1

                    # Update hash index
                    rel_ref = str(destination.relative_to(output_path))
                    hash_index[category][h] = rel_ref
                    logging.info(f"Moved file {file.name} to {destination}/")

                except Exception as e:
                    failed_files += 1
                    logging.error(f"Error moving file {file.name}: {e}")

    # -------- SAVE HASH INDEX --------
    save_hash_index(hash_index)

    #----------file not moved------
    not_moved_files = total_file - (moved_files + failed_files)

    #-----------convert byte to MB------------
    total_size_mb = total_size/(1024*1024)

    # -------- FINAL LOGGING --------
    logging.info("File organizer finished")
    logging.info(f"Total files: {total_file}")
    logging.info(f"Moved files: {moved_files}")
    logging.info(f"Failed files: {failed_files}")
    logging.info(f"Not moved files: {not_moved_files}")
    logging.info(f"Total size: {total_size_mb:.2f} MB")
    logging.info("File organizer finished")

    # -------- FINAL PRINT --------
    print("\n--- File Transfer Report ---")
    print(f"Total files: {total_file}")
    print(f"Moved files: {moved_files}")
    print(f"Failed files: {failed_files}")
    print(f"Not moved files: {not_moved_files}")
    print(f"Total size: {total_size_mb:.2f} MB")
    print("Files organized successfully")


# -------- RUN PROGRAM --------
if __name__ == "__main__":
    organizer_file("Input", "output")
