from pathlib import Path

import matplotlib.pyplot as plt
from tqdm import tqdm

from endf_handling import ENDFHandling

endf_files = list(Path("scraping/endf_files_renamed").glob("**/*.endf"))

for endf_path in tqdm(endf_files, desc="Reading ENDF files", total=len(endf_files)):
    endf = ENDFHandling(endf_file_path=endf_path)

    material_name = endf.material_name

    scattering_subset = endf.get_subset(endf.absorption_mt)

    for key, value in scattering_subset.items():
        energy = value["energy"]
        cross_section = value["cross_section"]
        plt.plot(energy, cross_section, label=f"MT{key}")

    plt.title(f"Scattering cross-section for {material_name}")
    plt.loglog()
    plt.xlabel("Energy (eV)")
    plt.ylabel("Cross-section (barn)")
    plt.legend()
    plt.show()
