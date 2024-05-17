#!/usr/bin/env python3

# PROTEOME DISCOVERER MGF SCAN NUMBER REPAIR TOOL
# 2024 (c) Micha Johannes Birklbauer
# https://github.com/michabirklbauer/
# micha.birklbauer@gmail.com

# version tracking
__version = "1.0.0"
__date = "2024-03-11"

# REQUIREMENTS
# pip install pandas
# pip install openpyxl
# pip install pyteomics

#########################

docs = \
"""
DESCRIPTION:
A simple script to fix wrongly parsed scan numbers generated from Proteome
Discoverer. Takes one table (e.g. PSMs, CSMs, etc) as input in .xlsx or .csv
format plus the corresponding mgf spectra containing the spectra. Additionally
the column name storing the (wrong) scan numbers in the table has to be given.
By default the column name "First Scan" is used (used in MS Annika). For
non-standard mgf files a regex pattern for parsing the scan number from the
title can be supplied.
USAGE:
scan_nr_repair_tool.py [-d --data]
                       [-m --mgf]
                       [-c --colname]
                       [-p --pattern]
                       [-o --output]
required arguments:
    -d str, --data str
        Input data file to be fixed in .csv or .xlsx format.
    -m str, --mgf str
        Input spectra file in mgf format.
optional arguments:
    -c str, --colname str
        The column name of the column that holds the scan numbers in the input data file.
        Default: "First Scan"
    -p str, --pattern str
        Regex pattern to be used to get the scan number from the title if it can't be automatically infered.
        Default: "\\.\\d+\\."
    -o str, --output str
        Name of the output file.
        Default: Name of the input data file + "_fixed.xlsx"
    -h, --help
        Show this help message and exit.
    --version
        Show program's version number and exit.
"""

#########################

# import packages
import re
import argparse
import pandas as pd
from pyteomics import mgf

import warnings

from typing import Any
from typing import List
from typing import Dict
from typing import Tuple
from typing import BinaryIO

####### FUNCTIONS #######

# parse scan number from pyteomics mgf params
def parse_scannr(params: Dict, pattern: str, i: int) -> Tuple[int, int]:
    """Parses the scan number from the params dictionary of the pyteomics mgf
    spectrum.

    Parameters
    ----------
    params : Dict
        The "params" dictionary of the pyteomics mgf spectrum.

    pattern : str
        Regex pattern to use for parsing the scan number from the title if it
        can't be infered otherwise.

    i : int
        The scan number to be returned in case of failure.

    Returns
    -------
    (exit_code, scan_nr) : Tuple
        A tuple with the exit code (0 if successful, 1 if parsing failed) at the
        first position [0] and the scan number at the second position [1].
    """

    # prefer scans attr over title attr
    if "scans" in params:
        try:
            return (0, int(params["scans"]))
        except:
            pass

    # try parse title
    if "title" in params:

        # if there is a scan token in the title, try parse scan_nr
        if "scan" in params["title"]:
            try:
                return (0, int(params["title"].split("scan=")[1].strip("\"")))
            except:
                pass

        # else try to parse by patternq
        try:
            scan_nr = re.findall(pattern, params["title"])[0]
            scan_nr = re.sub(r"[^0-9]", "", scan_nr)
            if len(scan_nr) > 0:
                return (0, int(scan_nr))
        except:
            pass

        # else try parse whole title
        try:
            return (0, int(params["title"]))
        except:
            pass

    # return insuccessful parse
    return (1, i)

# reading spectra and generate a scan number mapping
def read_spectra(filename: str | BinaryIO, pattern: str = "\\.\\d+\\.") -> Dict[int, int]:
    """Reads an mgf file and maps the index of each spectrum in the file
    to its scan number.

    Parameters
    ----------
    filename : str | BinaryIO
        Filename or file object of the mgf file to be read by pyteomics.

    pattern : str, default = "\\.\\d+\\."
        Regex pattern to use for parsing the scan number from the title if it
        can't be infered otherwise.

    Returns
    -------
    mapping : Dict[int, int]
        The mapping of spectrum index to spectrum scan number.

    Examples
    --------
    >>> from scan_nr_repair_tool import read_spectra
    >>> mapping = read_spectra("data/example.mgf")
    >>> mapping[0]
    2
    """

    result_dict = dict()
    exit_code = 0

    with mgf.read(filename, use_index = True) as reader:
        for s, spectrum in enumerate(reader):
            scan_nr = parse_scannr(spectrum["params"], pattern, -(s + 1))
            exit_code += scan_nr[0]
            result_dict[s + 1] = scan_nr[1]
        reader.close()

    print(f"\nFinished reading {s + 1} spectra!")

    if exit_code != 0:
        warnings.warn(f"Reading spectra exited with non-zero exit code. Scan numbers for {exit_code} spectra could not be parsed.", RuntimeWarning)

    return result_dict

def repair_scan_numbers(filename_data: str, colname_scannr: str, filename_mgf: str, pattern: str = "\\.\\d+\\.") -> pd.DataFrame:
    """Repairs the scan numbers of the given input file.

    Parameters
    ----------
    filename_data : str
        Filename of the .csv or .xlsx file to repair scan numbers in.

    colname_scannr : str
        The name of the column that holds the scan numbers in the input data
        file.

    filename_mgf : str
        The filename of the mgf file.

    pattern : str, default = "\\.\\d+\\."
        Regex pattern to use for parsing the scan number from the title if it
        can't be infered otherwise.

    Returns
    -------
    fixed_data : pd.DataFrame
        A pandas dataframe of the input data file with fixed scan numbers.

    Examples
    --------
    >>> from scan_nr_repair_tool import repair_scan_numbers
    >>> df = repair_scan_numbers("data/example_proteome_discoverer_output.xlsx", "First Scan", "data/example.mgf")
    Finished reading 25520 spectra!
    >>> df["First Scan"]
    0          144
    1          273
    2          892
    3          909
    4         1293
             ...
    11949    31277
    11950    31286
    11951    31300
    11952    31324
    11953    33911
    Name: First Scan, Length: 11954, dtype: int64
    """

    ext = filename_data.split(".")[-1].strip()

    if ext == "csv":
        df = pd.read_csv(filename_data)
    elif ext == "xlsx":
        df = pd.read_excel(filename_data)
    else:
        raise ValueError(f"Unsupported file extension {ext} - please use a .csv or .xlsx file as input!")

    mapping = read_spectra(filename_mgf, pattern)

    df[colname_scannr] = df[colname_scannr].apply(lambda x: mapping[int(x)])

    return df

##### MAIN FUNCTION #####

def main(argv = None) -> pd.DataFrame:
    """Main function.

    Parameters
    ----------
    argv : list, default = None
        Arguments passed to argparse.

    Returns
    -------
    fixed : pd.DataFrame
        The input data with correct scan numbers as a pandas dataframe.

    Examples
    --------
    >>> from scan_nr_repair_tool import main
    >>> fixed = main(["-d", "data/example_proteome_discoverer_output.xlsx", "-m", "data/example.mgf"])
    Finished reading 25520 spectra!
    >>> fixed
           Checked                                 Sequence Crosslinker  ... Search Space A Matched Ions B  Search Space B
    0        False                 KGFADAR-AHKPGSATIALNKRAR         DSS  ...              8              2               3
    1        False                         RAGGPLR-SKQGKHGR         DSS  ...              3              0               5
    2        False  FARAGLAVASMKGK-ATPHINAEMGDFADVVLMPGDPLR         DSS  ...              7              1               3
    3        False         FGKVRPARMGDLK-VVEKCIMMAPEQYMWLHR         DSS  ...              2              1               4
    4        False                ATPLIRVMNGHIYRVPNR-ARAKLR         DSS  ...              1              0              16
    ...        ...                                      ...         ...  ...            ...            ...             ...
    11949    False       GGKLSHVQQAYAK-HSIAYKLMFTIGKDPVVANK         DSS  ...             11              1               8
    11950    False            ASSNNNSFSAIYKEWYEHKK-GTVKFGVK         DSS  ...              4              0              15
    11951    False       EIKDPR-LESVVKEKGPLVEYHAEWNHWPDVGMR         DSS  ...              9              0              10
    11952    False  AGGIKQIK-GAGLAKAGMNRVVGDHMGMLATVMNGLAMR         DSS  ...             17              2              13
    11953    False                   LGGIGKK-IPLIIGRGLTTKAR         DSS  ...             19              1               4

    [11954 rows x 49 columns]
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data",
                        dest = "df",
                        required = True,
                        help = "Input data file to be fixed in .csv or .xlsx format.",
                        type = str)
    parser.add_argument("-m", "--mgf",
                        dest = "mgf",
                        required = True,
                        help = "Input spectra file in mgf format.",
                        type = str)
    parser.add_argument("-c", "--colname",
                        dest = "colname",
                        default = "First Scan",
                        help = "The column name of the column that holds the scan numbers in the input data file.",
                        type = str)
    parser.add_argument("-p", "--pattern",
                        dest = "pattern",
                        default = "\\.\\d+\\.",
                        help = "Regex pattern to be used to get the scan number from the title if it can't be automatically infered.",
                        type = str)
    parser.add_argument("-o", "--output",
                        dest = "output",
                        default = None,
                        help = "Name of the output file.",
                        type = str)
    args = parser.parse_args(argv)

    if args.output is None:
        output = args.df + "_fixed.xlsx"
    else:
        output = args.output + ".xlsx"

    fixed = repair_scan_numbers(args.df, args.colname, args.mgf, args.pattern)
    fixed.to_excel(output)

    return fixed

######## SCRIPT #########

if __name__ == "__main__":

    m = main()
