import datetime,time

START_UTC='2026-11-01T00:41:00+00:00'
END_UTC='2026-11-01T03:41:00+00:00'
END=datetime.datetime.fromisoformat(END_UTC).timestamp()
def remaining(): return END-time.time()
def check():
    if remaining()<=0: raise RuntimeError('GUN_B2B_THREE_HOUR_WALL_CAP')
