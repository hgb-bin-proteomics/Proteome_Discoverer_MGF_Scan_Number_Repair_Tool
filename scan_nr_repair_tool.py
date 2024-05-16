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
def parse_scannr(params: Dict, i: int) -> Tuple[int, int]:
        """Main function.

        Parameters
        ----------
        argv : list, default = None
            Arguments passed to argparse.

        Returns
        -------
        product : int
            The product of given arguments.

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

        # else try parse whole title
        try:
            return (0, int(params["title"]))
        except:
            pass

    # return insuccessful parse
    return (1, i)

# reading spectra
def read_spectra(filename: str | BinaryIO, name: str) -> Dict[int, int]:
        """Main function.

        Parameters
        ----------
        argv : list, default = None
            Arguments passed to argparse.

        Returns
        -------
        product : int
            The product of given arguments.

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

    result_dict = dict()
    exit_code = 0

    print("Read spectra in total:")

    with mgf.read(filename, use_index = True) as reader:
        for s, spectrum in enumerate(reader):

            if (s + 1) % 1000 == 0:
                print(f"\t{s + 1}")

            scan_nr = parse_scannr(spectrum["params"], -s)[1]
            exit_code += scan_nr[0]
            result_dict[s] = scan_nr[1]

        reader.close()

    print(f"\nFinished reading {s + 1} spectra!")

    if exit_code != 0:
        warnings.warn(f"Reading spectra exited with non-zero exit code. Scan numbers for {exit_code} spectra could not be parsed.")

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

    p = my_product(args.f1, args.f2)
    print(f"The product of {args.f1} * {args.f2} = {p}")

    return p

######## SCRIPT #########

if __name__ == "__main__":

    m = main()
