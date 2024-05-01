import shutil
from pathlib import Path

from tqdm import tqdm

from endf_handling import ENDFHandling

endf_files = list(Path("endf_files").glob("**/*.endf"))

destination_folder = Path("endf_files_renamed")
destination_folder.mkdir(exist_ok=True, parents=True)

for endf_path in tqdm(endf_files, desc="Reading ENDF files", total=len(endf_files)):
    endf = ENDFHandling(endf_file_path=endf_path)

    endf_name = endf.get_endf_name()

    destination_path = destination_folder / Path(endf_name.lower() + ".endf")
    if destination_path.exists():
        continue

    shutil.copy(endf_path, destination_path)
