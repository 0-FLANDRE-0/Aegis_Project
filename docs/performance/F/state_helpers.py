"""Normalize only existing host-duration diagnostics, never simulation state."""
PERFORMANCE_FIELDS=['performance','profiler','lastBuildMs','lastAssessmentMs']
def clean(v):
 if isinstance(v,dict):return {k:clean(q)for k,q in v.items()if k not in PERFORMANCE_FIELDS}
 if isinstance(v,list):return [clean(q)for q in v]
 return v
