from datetime import datetime,timezone
import json
from pathlib import Path
P=Path(__file__).resolve().parent
START=datetime.fromisoformat('2026-10-31T23:35:00+00:00');END=datetime.fromisoformat('2026-11-01T02:35:00+00:00')
def remaining():return(END-datetime.now(timezone.utc)).total_seconds()
def check():
 if remaining()<=0:raise TimeoutError('B2A_THREE_HOUR_WALL_CLOCK_LIMIT_STOP_AND_REPORT')
if not(P/'TASK_CLOCK.json').exists():(P/'TASK_CLOCK.json').write_text(json.dumps({'startUtc':START.isoformat(),'deadlineUtc':END.isoformat(),'limitS':10800,'policy':'Conservative start includes instruction review. Stop tests at deadline, preserve completed evidence, no retuning.'},indent=2)+'\n')
