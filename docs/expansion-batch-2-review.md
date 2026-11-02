# `expand_batch_2.py` static review

The script was inspected without executing it. Its `new_examples` list was read as a Python literal with `ast.literal_eval`, then compared read-only with `data/financial_dataset.json`.

## Findings

- The list has **62** candidates, while the exception text says **“Expected 60 examples”**. The condition checks `len(new_examples) != 62`, so the present 62-item list passes despite the contradictory message.
- Of the 62 prompts, **61** overlap an existing instruction in the 255-record dataset after the script's `strip().lower()` comparison; **one** prompt is novel.
- Four overlapping prompts have different responses: “What is a recurring deposit?”, “What is a secured loan?”, “What is an unsecured loan?”, and “What is a credit report?”
- The merge loop checks normalized instruction text only. If a prompt already exists, it silently skips the incoming record and discards any different answer; it does not report or resolve the conflicting response.
- The instruction normalization is limited to trimming leading/trailing whitespace and lowercasing; it does not collapse internal whitespace or perform semantic near-duplicate detection.
- The script loads `data/financial_dataset.json` and writes the combined list back to that same path. It has no backup, versioned output, atomic write, or overwrite confirmation.
- Some content concerns jurisdiction- or product-dependent banking, payments, loans, and tax matters that need current source verification before inclusion.

## Disposition

Do **not** run or merge this script as-is. It can overwrite the existing dataset, silently discard four conflicting responses, and hide near-duplicates behind a narrow exact-instruction check. Keep it as an unexecuted historical artifact; any future candidate should go through review and a new, non-overwriting canonical build.
