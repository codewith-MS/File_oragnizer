from pathlib import Path
import shutil

output_folder = Path("output")
input_folder = Path("input")

# -------- UNDO FUNCTION --------
for category_folder in output_folder.iterdir():
    if category_folder.is_dir():
        for file in category_folder.iterdir():
            if file.is_file():
                # Move file back to input folder
                shutil.move(str(file), str(input_folder / file.name))

print("Undo operation completed. All files moved back to input folder.")               