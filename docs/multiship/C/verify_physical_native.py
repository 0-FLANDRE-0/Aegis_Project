"""Inherited B source/damage native fixture at 8x; no forced render or geometry jobs.

SwiftShader's low wall-clock frame rate can consume the original 120-second
1x tick wait on a busy host. Only native time scale is changed, before unpause.
All physical/source/damage assertions are inherited unchanged from B.
"""
from pathlib import Path
source=Path(__file__).resolve().parent.parent/'B/verify_native.py'
text=source.read_text()
needle="window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false)"
assert text.count(needle)==2
text=text.replace(needle,"window.__NAVAL_SIM_DIAG__.setTimeScale(8);"+needle)
exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})
