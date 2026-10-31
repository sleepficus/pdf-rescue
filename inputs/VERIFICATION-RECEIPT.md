# Independent verification receipt — online PDF reconstruction investigation

Date: 2026-09-29

## Composer terminal state

- queue: `online-pdf-reconstruction-readiness-2026`
- run: `run-0001`
- started: `2026-09-29T11:50:03Z`
- finished: `2026-09-29T12:18:55Z`
- observed wall time: 1,732 seconds (28m 52s)
- stages: 15 `COMPLETED`
- seats: 15 `VERIFIED`
- failed/pending/skipped/uncertain: 0/0/0/0
- attempts: one per seat
- outputs: 15 `RESULT.md`
- terminal markers: 15 `TERMINAL.json`
- stage manifests: 15 `STAGE-MANIFEST.json`
- every terminal exit code: 0
- every required output: present and hash-matched
- every `via_fallback`: false

## Exact routes

| Wave | Seats | Requested/resolved model | Result |
|---|---:|---|---|
| MiMo scan | 5 | `opencode/mimo-v2.6-flash-free` | 5 verified |
| DeepSeek architecture | 5 | `opencode-go/deepseek-v4.1-flash` | 5 verified |
| SWE readiness | 5 | `swe-2-high` | 5 verified |

## Output hashes

| Stage | SHA-256 of `RESULT.md` |
|---|---|
| `m01-contradictions` | `a543ef7a42231cf9fb2a5c082ce63e0d4f7433d5684237e530cc67a57fa50eae` |
| `m02-scenarios` | `d4c7b4d0d38c31c5b9f4b932f61ae56f6b65186c22cca32fff10e49a5fe87870` |
| `m03-verification` | `1dc858ebaddfe9a397428f2412ab574c18400fe03fca3601f7d929d0016bab97` |
| `m04-fixtures` | `31cb130674a6084cd5b23d8c05e6b81ab2001ece5739a7b2a1f2f917559a749c` |
| `m05-batch-privacy` | `3468769f186f338a9336f0fd02c2abe50818a1ec9f3b319f290613ec11753d29` |
| `d01-modules` | `d2f6ad78935758dc0a5cddc1db4545d68de469245b9951385fef809abcf24a98` |
| `d02-disposition` | `5d0d312da84ce049c7823a322ce27a01a4e4291d5565ac5673c1e901a03386e0` |
| `d03-verification` | `f45e7e25924851be002c873e776972e24f94aa392b011d858229e5e2bc62a257` |
| `d04-review-ux` | `4daffc047c3835cfa2ecec7d81576cd7cdae3328f5a35bab4d4ae64bab2fb0b0` |
| `d05-batch-execution` | `6b54968e61f4f2e35f10cd6aa8179f0ccc0b35a7649deaf51ea69c47dc46e6ee` |
| `s01-dependencies` | `8444a5df06f8f5f95d17e044f7d5188861f89d6f9b798d2c198197158db6edf8` |
| `s02-work-breakdown` | `12939f4db59b1d7cd25a7974016ca7d97b2d002c2683fa56c48571941b760980` |
| `s03-test-harness` | `cebbfeb7130d2c27f8466e38fbaba2724a19b97ba5c35eb13220a90740db516e` |
| `s04-security` | `85fdacbac8e2385f65669a6187861322499654369ba427964b86a307281967e1` |
| `s05-integration` | `ae70b3069a94a193111085c48238305bdaf4923964944dedcab3268e1eb8c739` |

Each hash was independently recomputed from the final file and compared to its
sealed stage manifest.

## Frozen inputs

- source capsule: 19/19 files matched recorded byte sizes and SHA-256 values;
- capsule `data/`: zero files, as expected;
- `MAIN-GLM-SYNTHESIS.md`:
  `8d2a7d5b2ca703e26e41cc6e5f1e2ff52ef42923eb770f920069c2f18cfda872`;
- `COMPOSER-INPUT.md`:
  `1b8dc561d99363e04cdcbbe994ddace90fdfccb2ea0c8d4f9b378f0695840ed6`.

## GLM investigation receipts

- five successful exact `glm-5.3-flashx` lanes;
- one preserved first forms attempt ending in HTTP 429;
- successful observed wall span: 831.189 seconds (13m 51.189s);
- successful runner-duration sum: 1,770.478 seconds;
- provider responses: 91;
- prompt/completion/total tokens: 227,436 / 2,754 / 230,190;
- cached prompt tokens: 223,040;
- all five successful lanes wrote and verified `GLM-REPORT.md`,
  `GLM-DECISIONS.json`, and `FINAL.md`.

## Verification conclusion

The evidence chain is complete for an implementation-readiness investigation.
It is not evidence that a PDF reconstruction product has been implemented or
that any reconstruction behavior works on real documents.
