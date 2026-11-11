# Infrastructure Policy Lab handbook

By Jason Stys.

Build resource drift/replacement worklists and semantic-plan-bound reasoned review receipts.

Makes proposed infrastructure changes easier to assess without letting review annotations override policy gates.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [change review](change-review.md)
- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)

### Security and validation

- [security](security.md)
- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`5db2c9db4fd02cdff61eb4c98ea489ae2d9b48e6`](https://github.com/JasonStys/infrastructure-policy-lab/tree/5db2c9db4fd02cdff61eb4c98ea489ae2d9b48e6). The observed functional workflow baseline is `5db2c9db4fd02cdff61eb4c98ea489ae2d9b48e6`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/change-review-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/infrastructure-policy-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Reviewer/ticket context is asserted rather than authenticated.
- Review receipts cannot authorize deployment or override fail, unknown or review-needed policy states.
- Plan-bound review is not automatic infrastructure provisioning or a complete security/compliance certification.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

## Native graphical application

[First-use controls, supported workflows, profile/retention safety and actual portable acceptance](native-application.md) describe the new real application. [Dated observations](reports/native-application-2026-11-10.md) remain distinct from historical publications and pending release/installation.
