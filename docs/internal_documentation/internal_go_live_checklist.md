# Internal Go-Live Checklist

Use this checklist before colleagues start relying on the SDK internally.

## Status Legend

- [x] Done
- [ ] Not started
- [!] Won't do / intentionally deferred

## Already Covered

- [x] Scenario flows are already covered by [tests/integration/test_scenarios_integration.py](../tests/integration/test_scenarios_integration.py)
- [x] Public lookup gaps identified in [docs/missing_methods_analysis.md](missing_methods_analysis.md) have been implemented for the high-priority cases
- [x] Docs are reachable from the repo root via [open-documentation.cmd](../open-documentation.cmd)

## Must Do Before Go-Live

- [x] Run the full unit test suite in the project venv
- [x] Run the integration suite with valid ROAK credentials
- [x] Verify the generated docs build cleanly with Sphinx
- [x] Harden HTTP behavior in the client layer with timeouts and retry/backoff for transient failures
- [x] Standardize exceptions and error messages so users get predictable failures
- [x] Confirm auth, token refresh, and request retry behavior in the current environment
- [x] Review any remaining failing or skipped tests and decide whether they are acceptable for internal use
- [x] Decide which environment variables must be documented for your team
- [x] Confirm supported Python version and install path for internal users

## Should Do Before Go-Live

- [!] Add CI to run tests on every pull request
- [!] Add linting and type checks to CI
- [!] Pin dependency versions or ranges in a release-friendly way
- [x] Document common setup and auth issues for internal users
- [!] Define a rollback or hotfix process if a release causes problems

## Nice To Have

- [!] Add a release checklist for maintainers
- [!] Add changelog entries for user-visible changes
- [!] Add a short internal onboarding note that links to the docs launcher

## Exit Criteria

You are ready for internal go-live when:

- The unit tests pass
- The integration tests pass in the internal test environment
- The docs build succeeds
- The main usage flows are covered by automated tests
- The team knows how to open the docs and how to report issues


NOTES

Pin and document supported Python and dependency versions so colleagues don’t hit environment drift.
