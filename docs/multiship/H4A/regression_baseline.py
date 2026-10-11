"""Run H4 paired ownship regression directly against H4A."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE.parent/'H4/regression_baseline.py').read_text().replace('H3/H4','H4/H4A').replace('AEGIS_MULTI_SHIP_H4_BASELINE_COMPARISON','AEGIS_MULTI_SHIP_H4A_BASELINE_COMPARISON')
scope={'__file__':str(HERE.parent/'H4/regression_baseline.py'),'__name__':'_h4a_baseline'}
exec(compile(source,scope['__file__'],'exec'),scope)
if __name__=='__main__':scope['main']()
