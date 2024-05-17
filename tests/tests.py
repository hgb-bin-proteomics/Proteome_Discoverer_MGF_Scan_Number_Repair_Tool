#!/usr/bin/env python3

# PROTEOME DISCOVERER MGF SCAN NUMBER REPAIR TOOL - TESTS
# 2023 (c) Micha Johannes Birklbauer
# https://github.com/michabirklbauer/
# micha.birklbauer@gmail.com

def test1():

    from scan_nr_repair_tool import main

    assert main(["-d", "example_proteome_discoverer_output.xlsx",
                 "-m", "example.mgf"])["First Scan"][0] == 144
