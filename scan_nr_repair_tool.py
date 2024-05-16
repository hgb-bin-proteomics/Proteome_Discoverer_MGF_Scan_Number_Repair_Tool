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
A description of the script [multiplies two integers].
USAGE:
main.py [-f1 --factor1]
        [-f2 --factor2]
required arguments:
    -f1 int, --factor1 int
        First factor of multiplication.
optional arguments:
    -f2 int, --factor2
        Second factor of multiplication.
        Default: 2
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
            scan_nr = re.sub("[^0-9]", "", scan_nr)
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
def read_spectra(filename: str | BinaryIO, pattern: str = "\.\d+\.") -> Dict[int, int]:
    """Reads an mgf file and maps the index of each spectrum in the file
    to its scan number.

    Parameters
    ----------
    filename : str | BinaryIO
        Filename or file object of the mgf file to be read by pyteomics.

    pattern : str, default = "\.\d+\."
        Regex pattern to use for parsing the scan number from the title if it
        can't be infered otherwise.

    Returns
    -------
    mapping : Dict[int, int]
        The mapping of spectrum index to spectrum scan number.

    Examples
    --------
    >>> from main import read_spectra
    >>> mapping = read_spectra("data/example.mgf")
    >>> mapping[0]
    2
    """

    result_dict = dict()
    exit_code = 0

    with mgf.read(filename, use_index = True) as reader:
        for s, spectrum in enumerate(reader):
            scan_nr = parse_scannr(spectrum["params"], pattern, -s)
            exit_code += scan_nr[0]
            result_dict[s] = scan_nr[1]
        reader.close()

    print(f"\nFinished reading {s + 1} spectra!")

    if exit_code != 0:
        warnings.warn(f"Reading spectra exited with non-zero exit code. Scan numbers for {exit_code} spectra could not be parsed.", RuntimeWarning)

    return result_dict

##### MAIN FUNCTION #####

def main(argv = None) -> int:
    """Main function.

    Parameters
    ----------
    argv : list, default = None
        Arguments passed to argparse.

    Returns
    -------
    product : int
        Exit code of the main function (0 for success, 1 for error).

    Examples
    --------
    >>> from main import main
    >>> product = main(["-f1", "1", "-f2", "2"])
    >>> product
    2
    >>> product = main(["-f1", "3"])
    >>> product
    6
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-f1", "--factor1",
                        dest = "f1",
                        required = True,
                        help = "First factor of multiplication.",
                        type = int)
    parser.add_argument("-f2", "--factor2",
                        dest = "f2",
                        default = 2,
                        help = "Second factor of multiplication.",
                        type = int)
    args = parser.parse_args(argv)



    return

######## SCRIPT #########

if __name__ == "__main__":

    m = main()
