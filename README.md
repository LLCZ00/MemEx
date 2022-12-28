# MemEx
### _Memory Extractor_
MemEx is a script for extracting exectutables from memory. Specifically, it was intended for retrieving unpacked executables from the process memory of packed binaries, and dumping processes which have deleted their calling executable.

Currently only compatible with Linux.
## Usage
```
usage: memex.py [-h] [--version] [-p PID] [-i EXE] [-o FILE]
optional arguments:
  -h, --help            show this help message and exit
  --version             Show version number and exit
  -p PID, --pid PID     Process ID to extract executable from
  -i EXE, --input-exe EXE
                        Run given file/command/executable and extract from memory
  -o FILE, --output FILE
                        Write output to path/file (Default: ./output.dump)
Examples:
	memex.py -p 23263
	memex.py -o sus --pid 23465
	memex.py -i "./sus --config /home/user/config.txt"
```
MemEx can be given the PID of an active process, or run and dump a given executable directly. Arguments can be passed along with the executable by surrounding the whole command in quotes, as per example #3.

Root privilages are required to access the memory of other processes.
## Known Issues & TODO
- Add more process-specific features
	- Summary of frequently visited /proc/<pid> files, general malware analysis QoL stuff
	- A way to extract/carve only specific sections of the process's memory
- Windows version (maybe)
- There is currently a 0.5 second delay built in when starting a new process, to allow time for it to unpack itself. I haven't done extensive testing with the times so it may not be optimal, or even the best solution.
	- Add way to customize the delay time
- Might change *-i* to a positional argument, depending on if/how future features are handled
