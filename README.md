# ENDF handling 

## Overview 

ENDF (Evaluated Nuclear Data File) is a standardized data format for handling nuclear data such as cross-sections for different isotopes. The  file format is based on tape data formats, using columns and line numbers. For example, the start of MT2 (elastic scattering) for H-1 is shown below. Columns 75 - 80 are the line number, with `99999` indicating the start of a new section, 70 - 72 is the MF number (data type, like general information, cross-sections, resonance information etc.), and 72 - 75 is the MT (the reaction number, for example elastic scattering, fission etc.) For a full overview, see [this list](https://www.nndc.bnl.gov/endf/help.html#reaction). After the header, the data starts, with the energy (in eV), and the cross-section (in barn, so 1e-28 m$^2$) alternates. 

```
                                                                   125 3  099999
 1001.00000 .999167300          0          0          0          0 125 3  2    1
 0.0        0.0                 0          0          1        218 125 3  2    2
        218          2                                             125 3  2    3
 1.00000E-5 1159.660431.103037E-5 1104.184651.216691E-5 1051.36419 125 3  2    4
 ```

Aside from the peculiar data format, there are some more catches - empty lines, varying floating point and scientific notation formats, and duplicate entries. If you're used to more readable file-formats like JSON, CSV etc., this takes some getting used to. There are various existing ENDF handling libraries in Python, Fortran, C++ etc., but I found it interesting to create my own. 

## Features 

### Loading in data

We start by creating a class object by pointing at a particular data file. This loads the ENDF file into a dictionary. 

```
from endf_handling import ENDFHandling 

endf_file_path = Path("scraping/endf_files_renamed/h-1.endf")
handler = ENDFHandling(endf_file_path=endf_file_path)
```

This dictionary can then be saved as a JSON. 

```
handler.to_json("h-1.json")
```

If the name of the ENDF file is unknown, it can be read in with 

```
handler.get_endf_name()
>H-1
```

### Data aggregation 

ENDF files have hundreds of MTs. I have created some tools to aggregate these, combining different sources of scattering and absorption together. The ```absorption_mt``` is the range MT101 to 117, which includes various absorption reactions. Any list or range can be passed here, however. This interpolates all different MTs in this range to the same set of energies, and returns those and the associated cross-sections. 

```
absorption_mts = handler.absorption_mt
energies, cross_sections = handler.aggregate_mts(mt_range=absorption_mts)
```

### Subsets

Subsets containing multiple MTs can be retrieved with 

```
handler.get_subset([2, 18])
```

This returns a dictionary for the different MTs (using strings for the keys, not integers!), with two keys per MT: `energy` and `cross_section`. 

### Plotting

A specific MT or range of MTs can be plotted directly. 

```
handler.plot_mt_cross_sections(mt_range=[2])
```

This produces a plot like this: 

<img src="images/Example plotting two different MTs.png" width="400" alt="Plotting MT2 (elastic scattering) and MT18 (fission).">

## ENDF data 

I have mainly used EXFOR's [ENDF](https://www-nds.iaea.org/exfor/endf.htm) data repository so far, in combination with Brookhaven National Laboratory's [Sigma](https://www.nndc.bnl.gov/sigma/index.jsp). The latter provides human-readable data which is also interpolated etc. The raw ENDF data does not include resonances, and is generally very different from what you would want. It's possible to convert the ENDF files to have resonances etc. - there is a module available for that with [RECONR](https://docs.njoy21.io/projects/RECONR/en/docs/) as part of [NJOY21](https://github.com/njoy/NJOY21). However, this requires using various C++ tools and Fortran, which I do not have experience with. 

Luckily, there are also ready-made, point-wise evaluated ENDF files available. Sigma shows these by default, and in EXFOR, there is a button for exporting the individual reactions as JSON, but that is painful to do manually. 

Instead, it's possible to extract _all_ the point-wise evaluated ENDFs directly, without difficult processing. By using the following request, all available isotopes with some neutron cross-section data are put on a single page. Saving this page as a HTML as `scraping/source.html`, we can run a regex over this to extract all `EvalID` values. This can be done with `endf_webscraping.py`, which downloads all the ENDFs to `scraping/downloaded_endf_files/`, then saves a renamed copy into `scraping/endf_files_renamed`, in total around 11 GB of data. There is a built-in timer to only request one ENDF per ~5 s to limit load on the server. 

<img src="images/EXFOR ENDF data request form.png" width="800" alt="ParaView visualization of a reactor consisting of five 94% U-235 plates.">
