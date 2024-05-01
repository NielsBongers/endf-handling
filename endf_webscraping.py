import os
import random
import re
import shutil
import time
from pathlib import Path

import requests
from tqdm import tqdm

from endf_handling import ENDFHandling

endf_webpage = "scraping/source.html"

eval_id_list = []

with open(endf_webpage) as f:
    for line in f:
        pattern = r" PEN <\/a><a href=\"E4sGetEvaluation\?Pen=2&amp;EvalID=([0-9]+)\n"

        results = re.findall(pattern, line)

        if len(results) > 0:
            eval_id_list.append(results[0])

base_url = "https://www-nds.iaea.org/exfor/servlet/E4sGetEvaluation?Pen=1&EvalID="
request_urls = [base_url + eval_id for eval_id in eval_id_list]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

save_dir = Path("scraping/downloaded_endf_files")
save_dir.mkdir(exist_ok=True, parents=True)

for index, url in enumerate(tqdm(request_urls, desc="Downloading files")):
    filename = save_dir / Path(f"file_{index}.endf")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    time.sleep(random.uniform(1.0, 10.0))
    break

endf_files = list(save_dir.glob("**/*.endf"))

destination_folder = Path("scraping/endf_files_renamed")
destination_folder.mkdir(exist_ok=True, parents=True)

for endf_path in tqdm(endf_files, desc="Reading ENDF files", total=len(endf_files)):
    endf = ENDFHandling(endf_file_path=endf_path)

    endf_name = endf.get_endf_name()

    destination_path = destination_folder / Path(endf_name.lower() + ".endf")
    if destination_path.exists():
        continue

    shutil.copy(endf_path, destination_path)
