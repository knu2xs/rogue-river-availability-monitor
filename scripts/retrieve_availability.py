#!/usr/bin/env python
# coding: utf-8
import sys

from pathlib import Path

# paths to useful resources
dir_prj = Path.cwd().parent
dir_src = dir_prj / 'src'
dir_data = dir_prj / 'data'
dir_raw = dir_data / 'raw'

# location where partitioned output will be saved
out_dir = dir_raw / 'rogue_retrieved_availability'

# relative module import in case module is not installed
sys.path.insert(0, str(dir_src))
from rogue_river_spaces_monitor import save_rogue_availability_local

# save the local current state
save_rogue_availability_local(out_dir)
