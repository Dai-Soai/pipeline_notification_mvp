# Pipeline Notification MVP

Pipeline Notification MVP receives pipeline execution reports, classifies events,
builds notification messages, prepares channel payloads, and exports notification
artifacts.

---

## Features

- Load execution report JSON
- Classify pipeline events
- Build notification messages
- Generate channel payloads
- Preview notifications from CLI
- Export notification report as JSON

---

## Project Structure

pipeline_notification/
├── contract.py          # Notification contracts
├── loader.py            # Execution report loader
├── classifier.py        # Event classifier
├── message_builder.py   # Notification message builder
├── channel_payload.py   # Channel payload builder
├── report.py            # Notification report exporter
└── cli.py               # CLI interface

---

## Module Responsibilities

### contract.py

Defines:

- NotificationEvent
- NotificationMessage
- ChannelPayload
- NotificationReport

Responsible for notification data contracts only.

---

### loader.py

Loads execution report JSON.

Responsible for:

- validation
- normalization
- parsing

---

### classifier.py

Transforms execution report into notification events.

Responsible for:

- severity
- event type
- notification trigger

---

### message_builder.py

Creates human-readable notification messages.

Responsible for:

- title
- body
- severity
- metadata

---

### channel_payload.py

Creates channel-specific payloads.

Examples:

- console
- telegram
- webhook

---

### report.py

Builds notification report.

Responsible for:

- summary
- JSON export
- notification artifact

---

### cli.py

User interface.

Commands:

preview

Options:

--verbose

--json

--output

---

## Example

Preview

```bash
pipeline-notification preview data/sample_execution_report.json
```

Verbose

```bash
pipeline-notification preview \
    data/sample_execution_report.json \
    --verbose
```

Export JSON

```bash
pipeline-notification preview \
    data/sample_execution_report.json \
    --json \
    --output outputs/notification_report.json
```

---

## Tests

```bash
pytest
```

Current:

```
67 passed
```

---

## Release

Current version:

```
v0.1.0
```
