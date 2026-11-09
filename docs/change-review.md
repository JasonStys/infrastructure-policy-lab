# Digest-bound infrastructure change review

Created by Jason Stys. A platform owner can pass selected infrastructure checks and still need a change review; a destructive proposal cannot become safe just because someone acknowledges it. `worklist` and `review` keep those two facts separate.

```bash
mkdir -p out
python -m assurance worklist examples/destructive.json --out out/change-work
# Copy out/change-work/decisions-template.json to a private editable decisions.json.
# Add one explicit decision for each required resource; keep both digests unchanged.
python -m assurance review examples/destructive.json --decisions decisions.json --out out/change-receipt
```

The HTML worklist identifies create/update/delete, both replacement orders, read/no-op and drift-only resources. Each item retains selected findings and why review is needed. Any proposed mutation or non-PASS finding requires review; passing no-op/read items do not. Unsupported resources and sensitive/unknown checks keep their original UNKNOWN status. Worklist output includes a blank `decisions-template.json`; no approvals are prefilled.

The template contract is `schema: 1`, `plan_digest`, `worklist_digest`, `decisions: []`. Each decision requires `address`, `decision` (`acknowledged`, `defer`, `reject`), `reviewer`, `ticket`, and `reason`. For example:

```json
{"address":"aws_vpc.lab","decision":"defer","reviewer":"Fictional platform owner","ticket":"CHG-201","reason":"Replacement requires a reviewed recovery and maintenance plan."}
```

Use addresses from your generated worklist, not the illustrative one above. Empty/whitespace-only context, unknown/duplicate addresses, stale digests, unexpected fields and unsupported decisions are rejected. Reviewer context is bounded; do not include credentials or private plan values in notes. Plans remain bounded by the existing strict reader (8 MiB, 2,000 managed changes), and decisions by 4,000 entries to cover additional drift-only resources.

The command recomputes both the semantic plan identity and current worklist identity before accepting decisions. Formatting-only JSON changes retain semantic identity; configuration, action, drift or worklist changes invalidate an earlier receipt. Hashes are local identity checks, not authentication or plan freshness proof. Reviewer names/tickets are assertions, not signatures or access control.

Partial review is useful: receipts list every unreviewed required address. `all_required_reviewed` means a disposition was recorded; `all_required_acknowledged` additionally excludes defer/reject decisions. Neither changes the original `allowed`, counts or findings. A fully acknowledged destructive/unknown/failing plan stays blocked. There is no apply, cloud API, arbitrary shell or deployment authorization. `worklist` exit 0 means the selected-control gate passes, not that humans reviewed it; `review` exit 0 requires that gate plus complete acknowledgements. Exit 1 is blocked/incomplete/deferred/rejected review, while still exporting evidence; exit 2 rejects input/output.

New-directory-only output contains `review.json`, escaped scriptless `review.html`, and the empty template. Raw plan values and sensitive values never enter generated worklist findings; only selected metadata, digests and deliberately entered reviewer context appear. Keep real plans, decisions and reports private. Original Terraform mock-plan/OPA agreement checks remain unchanged. Worklist construction is linear in validated resources/findings plus deterministic sorting; there is no network or deployment side effect.
