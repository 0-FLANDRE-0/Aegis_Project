# Lossless battle capture transport

The native `battle.js` sampler is unchanged. Its final test-only exporter may
represent repetitive association-return and observed-lineage records as ordered
columnar data. No records or fields are omitted. This is storage/transport only;
analysis first calls `battle.decode_capture()` to restore original objects.

For a rowset, `columns` lists the exact original key strings. Each encoded row
is `[presentKeyIndexes, ...values]`. Indexes follow that particular object's
original `Object.keys` order, rather than sorting keys. An absent key has no
index/value; a present null remains null. Strings are interned as `{"$": n}`
using the rowset's `strings` array. This marker occurs only in encoded cells,
not in the native record schema.

`LOSSLESS_ASSOCIATION_COLUMNAR_2` additionally uses shared `pairColumns` and
`componentColumns` to encode each return's selected pairs/components. Held plot
and held track arrays remain their original numeric arrays. Actual selected and
held fields still come from one native return. No solver is rerun.

`LOSSLESS_LINEAGE_COLUMNAR_1` similarly shares top-level, measurement, observed
and sigma columns. Repeated measurement models are held verbatim in a `models`
dictionary and referred to by index. Original model object keys and values are
restored; observed polar measurements, local IDs, covariance metadata and
timestamps are preserved.

Before exporting, the browser restores both record sets and compares the whole
result with its original `JSON.stringify` string. Both must be byte-identical,
including object-key order. `transportReceipt` records original/decoded SHA256,
byte count, record counts and zero omissions. The proof is captured before the
runner adds post-validation and separates source receipts/passive state; it is
not called a hash of Python's later JSON serialization. All original16 stored
captures also pass a Node-only roundtrip check with deep equality and identical
JavaScript JSON strings; `battle-final/TRANSPORT_ROUNDTRIP.json` records it.

To decode a raw file without running a browser or game:

```sh
python docs/contact/track/B_stabilization/decode_battle_capture.py INPUT.json.gz OUTPUT.json
```

The decoder also checks browser proof receipts and restored record counts.
Original non-columnar captures remain supported. The10MiB per-page limit still
applies to the stored uncompressed transport record. Normal gzip is then used
for repository artifacts. Native trace-ring overwrites, diagnostic capture
drops, game faults and unresolved battle results retain their separate meanings.

For larger diagnostic variants, a storage-only fallback wraps the complete
canonical transport JSON bytes in `LOSSLESS_GZIP_JSON_ENVELOPE_1`. Its
`jsonGzipBase64` decompresses to those exact bytes; original byte count/SHA256,
byte-identical roundtrip and zero omissions are explicit. The outer record
still must fit10MiB. No sampler/native function or browser export changes for
this fallback. The decoder first checks/unwraps it, then restores columnar
records. `battle-analysis/STORAGE_ENVELOPE_ROUNDTRIP.json` proves a13.75MiB
existing semantic record restores byte-for-byte from a2.32MiB envelope without
any native calls. This is lossless storage, not deletion or subsampling.

The first oldACTIVE saturation attempt failed this tooling budget before raw
persistence. Its historical result object is unavailable; its failure receipt
is retained and the identical pinned product/setup/helper is replayed. No game
result is inferred from that failed tool execution. The valid A raw capture is
reused because only transport changed, with product/setup/helper/source receipts
checked in the same final authority report.

The first large-only diagnostic attempt similarly exceeded the columnar record
budget before persistence (10,913,073bytes). Its result object was lost and its
tooling error receipt is retained. It is replayed with the same pinned product,
setup, helper, criteria and record fields using only the storage envelope
fallback. The failed tooling execution is not counted as a native game result.
