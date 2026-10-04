#!/usr/bin/env python3
"""Native renderer regression. Never force progress on the presentation queue."""
from pathlib import Path
import runpy,sys
sys.argv.extend(['--ship','DDG_119_LATE_FLIGHT_IIA'])
runpy.run_path(str(Path(__file__).with_name('verify_native_damage.py')),run_name='__main__')
