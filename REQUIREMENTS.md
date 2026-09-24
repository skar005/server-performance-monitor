# Server Performance Monitor — Requirements

## 1. System Purpose

The Server Performance Monitor collects host performance measurements,
stores historical measurements, detects high resource utilisation, and
provides current and historical system health information through a
web interface.

## 2. Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| REQ-001 | The system shall collect CPU utilisation measurements. | Test / demonstration |
| REQ-002 | The system shall collect memory utilisation measurements. | Test / demonstration |
| REQ-003 | The system shall collect disk utilisation measurements. | Test / demonstration |
| REQ-004 | The system shall persist collected measurements in SQLite. | Automated test |
| REQ-005 | The system shall detect CPU utilisation above its configured threshold. | Automated test |
| REQ-006 | The system shall detect memory utilisation above its configured threshold. | Automated test |
| REQ-007 | The system shall detect disk utilisation above its configured threshold. | Automated test |
| REQ-008 | The system shall record detected high-utilisation alerts. | Automated test / demonstration |
| REQ-009 | The system shall provide a current system-health status. | API test / demonstration |
| REQ-010 | The system shall provide recent historical measurements. | API test / demonstration |
| REQ-011 | The system shall display monitoring information through a web dashboard. | Demonstration |
| REQ-012 | The system shall provide controlled stress-test functionality for development and demonstration. | Demonstration |

## 3. Non-Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| NFR-001 | The system shall store measurements using a persistent local database. | Inspection / test |
| NFR-002 | Alert thresholds shall be configurable. | Code inspection |
| NFR-003 | Automated tests shall be repeatable without modifying the production database. | Automated tests |
| NFR-004 | The system shall use timezone-aware UTC timestamps. | Code inspection / test |
| NFR-005 | The system shall provide sufficient historical data for the dashboard's monitoring view. | Demonstration |

## 4. Verification Status

All requirements are currently implemented to some degree.

Automated verification currently covers:

- threshold detection
- threshold non-detection
- database table creation
- metric storage and retrieval

The API and dashboard requirements currently rely primarily on demonstration and
will be strengthened with automated API tests in a subsequent development step.

## 5. Traceability

The requirements are traced to implementation through the source code and
automated tests:

- Alert decision logic → `alerting.py`
- Monitoring and API implementation → `app.py`
- Alert verification → `tests/test_alerting.py`
- Database verification → `tests/test_database.py`

Future changes should update this document when requirements or verification
methods change.
