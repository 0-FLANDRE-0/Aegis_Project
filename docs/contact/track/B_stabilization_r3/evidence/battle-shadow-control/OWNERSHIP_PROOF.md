# Observed lifecycle task-ownership defect

The SHADOW/control observer is native/passive/RNG-exact to oldB (15/15). The following is an actual native Finalize invocation, with no new RF/NIS/KF query:

- step721 / 12.016667s: scheduled300000001 / TRACK_REACQUIRE finalizes receiver-local300000003.
- Before: confirmed=True, sensorAge=0, reacquiring=False, misses=0, reacquireHits=0, FCQ=0.991927385378.
- After: reacquiring=True, misses=2, reacquireHits=1, FCQ=0.495963692689.

Native returned the same track. The emitter task belongs to local001 while the accepted recipient is003. Its fresh file is placed into REACQUIRE with two synthetic consecutive-miss count and half FCQ by that foreign task type. No physical identity inference is needed to establish this mismatch.

Observed window12–26s on003/004: 101 foreign-reacquire Finalize calls, 92 fresh false→true transitions. These are transition appearances, not unique targets.

The specific oldB17→R217.6 firing delay is not wholly attributed to this trace: no tr003 foreign false→true transition occurs in16–17.6s here. Own scheduled reacquisition, actual dwell misses and later clear paths must retain their separate behavior.

Root will consider a separately validated, ACTIVE-only fresh foreign-task ownership guard. Existing-reacquiring, scheduled first/second hits and native miss behavior must remain unchanged. No such product edit is made by this observer or proof report. All prior R1/R2/R3 outcomes and unresolved failures remain preserved/unapproved.
