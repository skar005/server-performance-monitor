# Server Performance Monitor — Requirements and Verification

## 1. System Purpose

The Server Performance Monitor collects host performance measurements,
stores historical measurements, detects high resource utilisation, and
provides current and historical system health information through a
web interface.

## 2. Functional Requirements

| ID | Requirement |
|---|---|
| REQ-001 | The system shall measure CPU utilisation (%) in every collection cycle. |
| REQ-002 | The system shall measure memory utilisation (%) in every collection cycle. |
| REQ-003 | The system shall measure root-filesystem disk utilisation (%) in every collection cycle. |
| REQ-004 | The system shall persist every measurement in SQLite with a UTC timestamp. |
| REQ-005 | The system shall raise an alert when CPU utilisation exceeds 75%. |
| REQ-006 | The system shall raise an alert when memory utilisation exceeds 75%. |
| REQ-007 | The system shall raise an alert when disk utilisation exceeds 90%. |
| REQ-008 | The system shall store each alert with its timestamp, metric, value and message. |
| REQ-009 | The system shall report a current status of "healthy" or "warning", with the latest CPU, memory, disk, process count and host uptime. |
| REQ-010 | The system shall return the 100 most recent measurements in ascending time order. |
| REQ-011 | The system shall present current status, a history chart and recent alerts on a web dashboard that refreshes every 5 seconds. |
| REQ-012 | The system shall provide CPU and memory load simulation, each lasting 20 seconds, for demonstration and testing. |
| REQ-013 | The system shall collect a measurement every 15 seconds. |
| REQ-014 | The system shall record the process count and network bytes sent and received with every measurement. |
| REQ-015 | Status classification and alerting shall apply the same thresholds and the same comparison rule, including at exactly the threshold value. |
| REQ-016 | The system shall return the 10 most recent alerts, each with timestamp, metric, value and message. |

## 3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-001 | The system shall store measurements using a persistent local database. |
| NFR-002 | Alert thresholds shall be defined in one place and changeable without editing application logic. |
| NFR-003 | Automated tests shall run repeatably without modifying any development or deployed database. |
| NFR-004 | All timestamps shall be timezone-aware UTC. |
| NFR-005 | At the default interval, the dashboard history shall span at least 20 minutes. |
| NFR-006 | Measurement history shall survive redeployment of the application container. |
| NFR-007 | The deployed service shall restart automatically after a host reboot. |
| NFR-008 | A change shall be deployed only if the automated test suite passes. |

## 4. Verification Matrix

Status key: Verified = covered by an automated test or inspection;
Demonstrated = shown on the live system; Partial = some evidence, with
untested cases; Gap = nothing verifies it yet; Not met = known
non-compliance (see section 5).

| ID | Method | Evidence today | Status |
|---|---|---|---|
| REQ-001 to 003 | Test | No direct test of `collect_metrics`; fields seen indirectly in `test_metrics_endpoint` | Partial |
| REQ-004 | Test | `test_metric_can_be_stored` (database layer only) | Partial |
| REQ-005 | Test | `test_cpu_above_threshold`, `test_cpu_below_threshold` | Verified |
| REQ-006 | Test | `test_memory_below_threshold` only; no above-threshold case | Partial |
| REQ-007 | Test | `test_disk_above_threshold` only; no below-threshold case | Partial |
| REQ-008 | Test | Table creation tested; nothing checks that an alert row is written | Gap |
| REQ-009 | Test | `test_status_endpoint` checks fields, not healthy/warning logic | Partial |
| REQ-010 | Test | `test_metrics_endpoint` checks fields, not the 100-row limit or ordering | Partial |
| REQ-011 | Demonstration | Live dashboard screenshots | Demonstrated |
| REQ-012 | Demonstration | Stress test raised a CPU alert on the live dashboard | Demonstrated |
| REQ-013 | Test | None; interval is set in `app.py` | Gap |
| REQ-014 | Inspection | Columns in schema; stored in `test_metric_can_be_stored` | Partial |
| REQ-015 | Test | None; behaviour at the exact threshold is inconsistent (D1) | Not met |
| REQ-016 | Test | `test_alerts_endpoint` checks these fields only if alerts exist; endpoint omits metric and value (D2) | Not met |
| NFR-001 | Inspection | `database.py` uses a SQLite file | Verified |
| NFR-002 | Inspection | Thresholds hard-coded in `app.py` and `alerting.py` (D1) | Not met |
| NFR-003 | Test | `test_database.py` uses a temp DB; `test_api.py` does not (D3) | Not met |
| NFR-004 | Inspection | `datetime.now(timezone.utc)` in `app.py`; no test | Partial |
| NFR-005 | Test | Follows from REQ-010 (100 x 15 s = 25 min) | Partial |
| NFR-006 | Demonstration | Deploy script recreates the container without a volume (D4) | Not met |
| NFR-007 | Demonstration | No restart policy in the deploy script (D4) | Not met |
| NFR-008 | Inspection | `needs: test` in `.github/workflows/ci.yml` | Verified |

## 5. Defects and Gaps Found by Tracing

- D1: `app.py` and `alerting.py` each define their own thresholds. Status uses `<` and alerting uses `>`, so at exactly the threshold the dashboard shows "warning" but no alert is raised.
- D2: `/api/alerts` returns only timestamp and message. `test_alerts_endpoint` expects metric and value too, but only checks them when alerts exist, so it passes while the alerts table is empty.
- D3: `test_api.py` imports `app`, which starts the scheduler and writes a reading to `metrics.db` in the working directory at import time.
- D4: The deploy script runs `docker run` with no volume and no restart policy. Redeploying deletes measurement history, and a host reboot leaves the service stopped.

## 6. Traceability

| Area | Implementation | Tests |
|---|---|---|
| Alert decision | `alerting.py` | `tests/test_alerting.py` |
| Persistence | `database.py` | `tests/test_database.py` |
| Collection, API, dashboard | `app.py` | `tests/test_api.py` |
| Build, test, deploy | `.github/workflows/ci.yml`, `Dockerfile` | CI run on every push |

REQ-001 to REQ-012 and NFR-001 to NFR-005 keep their original IDs, with wording made measurable. Later IDs were added after tracing the requirements against the code and tests. Update this document whenever a requirement, test or deployment step changes.
