#!/usr/bin/env python3.6
import io
import re
import shutil
import os
from os import path
import sys

class unpacker:
    FILESIZE_RE = re.compile(r'filesizes="(\d+?)"')
    OFFSET_RE = re.compile(r'offset=`head -n (\d+?) "\$0"')

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def unpack(self):
        self.game_bin = open(self.input_path, "rb")
        os.makedirs(self.output_path, exist_ok=True)

        # Read the first 10kb so we can determine the script line number
        beginning = self.game_bin.read(10240).decode("utf-8", errors="ignore")
        offset_match = self.OFFSET_RE.search(beginning)
        script_lines = int(offset_match.group(1))

        # Read the number of lines to determine the script size
        self.game_bin.seek(0, io.SEEK_SET)
        for l in range(0, script_lines):
            self.game_bin.readline()
        script_size = self.game_bin.tell()
        print("Makeself script size:", script_size)

        # Read the script
        self.game_bin.seek(0, io.SEEK_SET)
        script_bin = self.game_bin.read(script_size)
        with open(path.join(self.output_path, "unpacker.sh"), "wb") as script_f:
            script_f.write(script_bin)
        script = script_bin.decode("utf-8")

        # Filesize is for the MojoSetup archive, not the actual game data
        filesize_match = self.FILESIZE_RE.search(script)
        filesize = int(filesize_match.group(1))
        print("MojoSetup archive size:", filesize)

        # Extract the setup archive
        self.game_bin.seek(script_size, io.SEEK_SET)
        with open(path.join(self.output_path, "mojosetup.tar.gz"), "wb") as setup_f:
            setup_f.write(self.game_bin.read(filesize))

        # Extract the game data archive
        dataoffset = script_size + filesize
        self.game_bin.seek(dataoffset, io.SEEK_SET)
        with open(path.join(self.output_path, "data.zip"), "wb") as datafile:
            shutil.copyfileobj(self.game_bin, datafile)

def main():
    input_path = ''
    output_path = ''
    if len(sys.argv) == 2:
        input_path = sys.argv[1]
        output_path = "./"
    elif len(sys.argv) == 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print("Usage: {} <input file> <output dir>".format(sys.argv[0]))
        exit(1)
    up = unpacker(input_path, output_path)
    up.unpack()

if __name__ == '__main__':
    main()

