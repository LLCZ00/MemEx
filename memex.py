#!/usr/bin/python3
#
# Copyright (C) 2022 LLCZ00
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.  
#
"""
memex.py - Extract executable from process memory
- Linux

References:
https://stackoverflow.com/questions/1401359/understanding-linux-proc-pid-maps-or-proc-self-maps
https://man7.org/linux/man-pages/man5/proc.5.html
"""
__VERS = "1.0.0"
import sys
import os
import re
import subprocess
import shlex
import logging
import argparse
from time import sleep


class ProcInfo: # This is kinda fugly
    def __init__(self, pid):
        self.pid = pid

    @classmethod
    def command(cls, exe_cmd, delay=0.5):
        """
        Start new process with given file/command, return ProcInfo instance with new process ID
        - Delay required to actually give the process time to unpack
        """
        proc = subprocess.Popen(shlex.split(exe_cmd))
        sleep(delay)
        logging.info(f"Process started ({proc.pid}): {exe_cmd}")
        return cls(proc.pid)


    def dump(self, output="output.dump"):
        """
        Extract process from memory, write to file
        - Process's currently mapped memory regions collected from /proc/<pid>/maps
        - Raw virtual memory accessed via /proc/<pid>/mem
        """
        with open(f"/proc/{self.pid}/maps", 'r') as maps_file, open(f"/proc/{self.pid}/mem", 'rb') as mem_file, open(output, 'wb') as output_file:
            for region in maps_file.readlines(): # Iterate through each mapped region
                address = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', region) # (start)-(end) (read_permission bit)
                if address.group(3) == 'r':
                    start_addr = int(address.group(1), 16) # Convert address strings to base 16 integer
                    end_addr = int(address.group(2), 16)
                    mem_file.seek(start_addr)
                    try:
                        chunk = mem_file.read(end_addr - start_addr) # Dump region contents into output file
                        output_file.write(chunk)
                    except OSError:
                        logging.info(f"Skipped: {region}")
                        continue
        print(f"[OK] Process ({self.pid}) dumped to: {output}") # ! Check if this was actually successful



class MemExParser(argparse.ArgumentParser):
    """Override argparse class for better error handler"""
    def error(self, message="Unknown error", help=False):
        if help:
            self.print_help()
        else:
            print(f"Error. {message}")
            print(f"Try './{self.prog} --help' for more information.")
        sys.exit(1)

class ValidatePID(argparse.Action):
    """argparse Action to validate existence of process"""
    def __call__(self, parser, namespace, value, option_string=None):
        if value is None:
            return # Do nothing if no value given

        if value.isdigit() is False:
            parser.error(f"Invalid Process ID '{value}'")

        if os.path.exists(f"/proc/{value}") is False:
            parser.error(f"Process ID not found '{value}'")

        setattr(namespace, self.dest, value)


def parse_arguments():
    """Get command line arguments"""
    parser = MemExParser(
    prog="memex.py",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Memory Extractor - Tool for carving/extracting packed executables from memory', 
    epilog='Examples:\n\tmemex.py -p 23263\n\tmemex.py -o sus --pid 23465\n\tmemex.py -i "./sus --config /home/user/config.txt"'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'MemEx {__VERS}',
        help='Show version number and exit'
    ) 
    parser.add_argument(
        '-p','--pid',
        metavar='PID',
        dest='pid',
        type=str,
        default=None,
        action=ValidatePID,
        help='Process ID to extract executable from'
    )
    parser.add_argument(
        '-i','--input-exe',
        metavar='EXE',
        dest='input_exe',
        type=str,
        default=None,
        help='Run given file/command/executable and extract from memory'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        dest='output',
        default='output.dump',
        help='Write output to path/file (Default: ./output.dump)'
    )
    
    args = parser.parse_args()

    if len(sys.argv) <= 1: # Display help menu if no args given
        parser.error(help=True)

    if os.getuid() != 0:
        parser.error("root privileges required.")

    if args.pid and args.input_exe:
        parser.error("Both PID and input executable were given.")

    return args


def main():
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
    args = parse_arguments()

    if args.input_exe:
        process = ProcInfo.command(args.input_exe)
    else:
        process = ProcInfo(args.pid)

    process.dump(args.output)


if __name__ == "__main__":
    sys.exit(main())

