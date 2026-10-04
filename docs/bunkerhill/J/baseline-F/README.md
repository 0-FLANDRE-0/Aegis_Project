# F comparison source

The small modules in this folder are unchanged copies from WIP BUNKERHILL F.
`rebuild_f_baseline.py` extracts the unchanged embedded assets from G/H and builds
F from the exact STARTUP A. It rejects any output whose SHA-256 differs from
`993ca479c3cee902348865cfbfca6567f3cec96297a8cd0b7d606c484b3a730c`.

F is used to reproduce the native draw freeze and the sparse VLS edit/preset bugs.
Its old controlled-queue 3D test is not a native frame regression.
