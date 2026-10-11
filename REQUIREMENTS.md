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
untested cases remaining; Gap = nothing verifies it yet; Pending demo =
implemented, awaiting demonstration on the deployed system.

| ID | Method | Evidence today | Status |
|---|---|---|---|
| REQ-001 to 003 | Test | No direct test of `collect_metrics`; fields seen indirectly in `test_metrics_endpoint` | Partial |
| REQ-004 | Test | `test_metric_can_be_stored` (database layer only) | Partial |
| REQ-005 | Test | `test_cpu_above_threshold`, `test_cpu_below_threshold`, plus boundary cases in `test_status_agrees_with_alerting_rule` | Verified |
| REQ-006 | Test | `test_memory_below_threshold`, plus above and at-threshold cases in `test_status_agrees_with_alerting_rule` | Verified |
| REQ-007 | Test | `test_disk_above_threshold`, plus below and at-threshold cases in `test_status_agrees_with_alerting_rule` | Verified |
| REQ-008 | Test | `test_alerts_endpoint_returns_full_alert_record` verifies stored fields; no test that `collect_metrics` writes the alert row | Partial |
| REQ-009 | Test | `test_status_endpoint` (fields) and `test_status_agrees_with_alerting_rule` (healthy/warning at boundaries) | Verified |
| REQ-010 | Test | `test_metrics_endpoint` checks fields, not the 100-row limit or ordering | Partial |
| REQ-011 | Demonstration | Live dashboard screenshots | Demonstrated |
| REQ-012 | Demonstration | Stress test raised a CPU alert on the live dashboard | Demonstrated |
| REQ-013 | Test | None; interval is set in `app.py` | Gap |
| REQ-014 | Inspection | Columns in schema; stored in `test_metric_can_be_stored` | Partial |
| REQ-015 | Test | `test_status_agrees_with_alerting_rule` (six boundary cases) | Verified |
| REQ-016 | Test | `test_alerts_endpoint_returns_full_alert_record` and `test_alerts_endpoint`; 10-row limit untested | Partial |
| NFR-001 | Inspection | `database.py` uses a SQLite file | Verified |
| NFR-002 | Test / inspection | Single definition verified by `test_thresholds_are_defined_in_one_place`; still changed by editing `alerting.py`, not externally configurable | Partial |
| NFR-003 | Test | `tests/conftest.py` redirects to a temporary database; `test_tests_do_not_use_the_working_directory_database` | Verified |
| NFR-004 | Inspection | `datetime.now(timezone.utc)` in `app.py`; no test | Partial |
| NFR-005 | Test | Follows from REQ-010 (100 x 15 s = 25 min) | Partial |
| NFR-006 | Test / demonstration | Configurable path verified by `test_db_path_is_configurable_by_environment`; named volume `monitor-data` in deploy script; survival of a redeploy not yet demonstrated | Pending demo |
| NFR-007 | Demonstration | `--restart unless-stopped` in deploy script; survival of a host reboot not yet demonstrated | Pending demo |
| NFR-008 | Inspection | `needs: test` in `.github/workflows/ci.yml` | Verified |

## 5. Defects Found by Tracing

| ID | Defect | Fix | Commit |
|---|---|---|---|
| D1 | Thresholds defined twice; status and alerting compared differently at the exact threshold | Single `THRESHOLDS` and shared `is_healthy` rule in `alerting.py` | 711ecfe |
| D2 | `/api/alerts` dropped metric and value; its test passed only because the table was empty | Endpoint returns the full record; new test seeds an alert | 6d97ca3 |
| D3 | Tests wrote to the working-directory database | `tests/conftest.py` redirects to a temporary database | acb62e3 |
| D4 | Redeploy deleted measurement history; no restart after host reboot | Configurable database path, `monitor-data` volume, restart policy | f1f8ae5 (demonstration pending) |

Each fix has a regression test, except the deployment parts of D4, which are verified by demonstration.

Remaining gaps:

- No direct test of `collect_metrics` (REQ-001 to 004, 013, 014, and the alert write path of REQ-008)
- Row limits and ordering untested for history and alerts (REQ-010, REQ-016)
- `test_alerts_endpoint` only checks fields when alerts exist, so its result depends on test order
- Thresholds are not externally configurable (NFR-002)

## 6. Traceability

| Area | Implementation | Tests |
|---|---|---|
| Alert decision and health rule | `alerting.py` | `tests/test_alerting.py`, `tests/test_threshold_consistency.py` |
| Persistence and configuration | `database.py` | `tests/test_database.py`, `tests/test_db_path_config.py` |
| Collection, API, dashboard | `app.py` | `tests/test_api.py`, `tests/test_alerts_api.py` |
| Test isolation | `tests/conftest.py` | `tests/test_isolation.py` |
| Build, test, deploy | `.github/workflows/ci.yml`, `Dockerfile` | CI run on every push |

REQ-001 to REQ-012 and NFR-001 to NFR-005 keep their original IDs, with wording made measurable. Later IDs were added after tracing the requirements against the code and tests. Update this document whenever a requirement, test or deployment step changes.
