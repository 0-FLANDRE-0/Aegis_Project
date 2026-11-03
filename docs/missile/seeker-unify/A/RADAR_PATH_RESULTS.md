# Managed and NPC radar path validation

**Result: PASS**

| path | baseline rows | product rows | baseline tracks | product tracks | changed conditions | truth refs |
|---|---:|---:|---:|---:|---:|---:|
| ownship managed radar acceptors | 420 | 420 | 255 | 255 | 0 | 0 |
| NPC observer radar/track store | 60 | 60 | 24 | 24 | 0 | 0 |

The managed test drives production SPY-1D(V), SPQ-9B and BridgeMaster-E
plot acceptors into the ownship TrackStore. The NPC test advances
`stepObserversC` and reads only each observer's anonymous track store.
Neither test treats a direct RF echo as a completed track.
