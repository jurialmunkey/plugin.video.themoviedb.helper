#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Quick and dirty script to clean up strings.po by reading ID from copied to clipboard and then delete lines from files
"""

from tkinter import Tk
import os


if __name__ == "__main__":

    z_string = 'msgctxt'

    files = [os.path.join(f.path, 'strings.po') for f in os.scandir('.') if f.is_dir()]

    a_number = Tk().clipboard_get()

    if a_number:

        a_string = f'msgctxt "#{a_number}"'

        for file in files:
            try:
                with open(file, encoding="utf8") as f:
                    lines = f.readlines()

                skip_range = None
                a_line = None
                z_line = None

                for x, line in enumerate(lines):

                    if not a_line:
                        if line.startswith(a_string):
                            a_line = x
                        continue

                    if line.startswith(z_string):
                        z_line = x
                        break

                try:
                    skip_range = [i for i in range(a_line, z_line)]
                except TypeError:  # Failure to get a line
                    print(f'{file}\nFAILED: {a_number} {a_line} {z_line}')
                    continue

                print(f'{file}\nDELETE: {skip_range}')
                with open(file, 'w', encoding="utf8") as f:
                    for x, line in enumerate(lines):
                        if x not in skip_range:
                            f.write(line)

            except FileNotFoundError:
                continue
