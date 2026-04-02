# ROAK SDK Testing Plan

## 1. Goals

- Prevent regressions in public SDK behavior.
- Validate request construction and response handling for API clients.
- Ensure semantic and facade classes enforce expected business rules.
- Make tests fast, deterministic, and independent from live ROAK environments.

## 2. Test Approach

- Use `pytest` as the test runner.
- Use `unittest.mock`/`pytest-mock` to mock HTTP requests and client calls.
- Keep unit tests isolated from real network calls.
- Add a small optional integration test layer (disabled by default) for real API validation.

## 3. Proposed Test Structure

- `tests/unit/clients/`
- `tests/unit/semantics/`
- `tests/unit/facade/`
- `tests/unit/auth/`
- `tests/integration/` (optional, environment-gated)
- `tests/conftest.py` (shared fixtures)

## 4. Priority Test Targets

### P0: Core User-Facing Behavior

- Name-based lookups with `allow_first_match=False`:
  - Raise when multiple matches exist.
  - Return single match when exactly one exists.
  - Raise when no matches exist.
- Name-based lookups with `allow_first_match=True`:
  - Return first matching result (current permissive behavior).
- Date-range handling in user-facing methods:
  - Accept timezone-aware `datetime`.
  - Accept epoch milliseconds (`int`).
  - Raise for missing start/end.
  - Raise for naive `datetime`.
  - Raise when start > end.

### P1: Semantic Attribute Refresh

- `Semantic.refresh_attributes`:
  - Calls semantic endpoint client with semantic GUID.
  - Reads `content` payload and maps `name -> value` into `_data`.
  - Handles missing `content` key as an error.
  - Preserves/updates `guid` and `name` when returned in payload.

### P1: Client Request Correctness

- `AssetClient.get_data`:
  - Sends `from`/`to` as milliseconds.
  - Forwards `feedNames` correctly.
- `RoakClient` and `ProjectClient` by-name methods:
  - Correct filtering by `name` and optional type.
  - Correct ambiguity behavior for `allow_first_match` flag.

### P2: Semantic Convenience Layers

- `Project.get_well_by_name` and `Project.get_borehole_by_name`:
  - Pass through `allow_first_match` and type filters correctly.
- `Rig.get_borehole_by_name`:
  - Local filtering, duplicate handling, and not-found handling.
- `Modem.get_data_through_children`:
  - Date normalization and child feed filtering behavior.

## 5. Fixtures and Test Data

Create reusable fixtures in `tests/conftest.py`:

- Minimal `ClientRegistry` with mocked headers/base URL.
- Mocked client instances (`AssetClient`, `ProjectClient`, `RoakClient`, `SemanticClient`).
- Sample semantic payloads:
  - Unique name result.
  - Duplicate name result.
  - Empty result.
  - Attributes page payload with `content` list.

## 6. Mocking Strategy

- Prefer mocking client methods at semantic/facade layers.
- For client unit tests, mock `requests.get` (or `BaseClient._request`) and assert:
  - URL path
  - query params
  - error handling branch behavior

## 7. Integration Tests (Optional)

- Add environment-gated integration tests that run only when credentials are set.
- Suggested env vars:
  - `ROAK_USERNAME`
  - `ROAK_PASSWORD`
  - `ROAK_BASE_URL`
  - `ROAK_TENANT` (optional)
- Mark with `@pytest.mark.integration` and skip by default.

## 8. Execution and Quality Gates

- Run all unit tests in CI on every PR.
- Use `pytest -q` for local runs.
- Add coverage target (initially 70%, then increase to 85%+).
- Fail CI on:
  - test failures
  - lint/type-check failures (if configured)

## 9. Suggested Rollout

1. Build fixtures and base test utilities.
2. Implement P0 tests first.
3. Implement P1 tests.
4. Add P2 and integration tests.
5. Enforce CI gates.

## 10. Definition of Done

- P0 and P1 tests implemented and green.
- New behavior (ambiguity guard + datetime/millis validation + semantic refresh) fully covered.
- Test suite is deterministic and runnable without network by default.

## 11. High-Value Additions (Next)

This section lists additional tests that provide the highest risk reduction per effort.

### HV1: Authentication correctness and failure handling

Targets:

- `src/roak_sdk/auth.py`

Add tests for:

- Constructor validation: missing username/password.
- `authenticate()` happy path (headers, tokens, expiry).
- `authenticate(force_refresh=False)` reuses cached headers.
- `authenticate(force_refresh=True)` performs new request.
- Request exception and non-200 mapping to `AuthenticationError`.
- Invalid JSON mapping to `InvalidJSONError`.
- `_select_access_token()` tenant and access list branches.
- `refresh_access_token()` full success/error matrix.
- `is_token_expired()` boundary behavior.

Value:

- Highest business risk path.
- Most likely source of production failures and hard-to-debug incidents.

### HV2: Base client retry and JSON parsing guarantees

Targets:

- `src/roak_sdk/clients/base_client.py`

Add tests for:

- Standard 200 JSON response path.
- 401 then refresh then retry success path.
- 401 with no refresh callback behavior.
- Invalid JSON handling raises `InvalidJSONError`.
- Time conversion helpers (`datetime_to_millis`, `millis_to_datetime`).

Value:

- Shared infrastructure for every API client.
- Prevents silent regressions in auth refresh and response parsing.

### HV3: Client registry lifecycle behavior

Targets:

- `src/roak_sdk/clients/client_registry.py`

Add tests for:

- Client caching (same class returns same instance).
- `update_headers()` propagates to existing clients.
- `refresh_tokens()` with callback updates headers and returns new headers.
- `refresh_tokens()` without callback returns `None`.

Value:

- Ensures token refresh behavior is consistent across all instantiated clients.

### HV4: Roak facade orchestration and type guards

Targets:

- `src/roak_sdk/roak.py`

Add tests for:

- Constructor wiring of Auth -> Registry -> RoakClient.
- `_refresh_tokens()` and `refresh_tokens()` behavior.
- Name-based methods pass `allow_first_match` correctly.
- `get_rig_by_name()` and `get_modem_by_guid()` type guard errors.
- Collection methods return expected semantic object types.

Value:

- Covers the public surface users call directly.

### HV5: Borehole transformation logic

Targets:

- `src/roak_sdk/semantics/assets/borehole.py`

Add tests for:

- `_pivot_depth_data()` grouping and sort order.
- Datetime conversion from timestamps.
- `_forward_fill_values()` for `None` and empty-string values.
- `get_depth_data()` integration of client response + pivot + fill.

Value:

- Complex data-shaping logic with real regression potential.

### HV6: Project filtering and factory mapping

Targets:

- `src/roak_sdk/semantics/project.py`
- `src/roak_sdk/semantics/factory.py`

Add tests for:

- `get_assets()` filters out unsupported `typeGuid` values.
- `make_asset()` returns Well/Borehole/Asset as expected.
- `get_asset_by_guid()` and `get_asset_by_name()` return correct semantic subtype.

Value:

- Ensures users receive the right runtime object and methods.

### HV7: Low-cost URL contract tests for thin clients

Targets:

- `src/roak_sdk/clients/device_client.py`
- `src/roak_sdk/clients/rig_client.py`
- `src/roak_sdk/clients/borehole_client.py`
- `src/roak_sdk/clients/semantic_client.py`

Add tests for:

- Correct endpoint path composition.
- Expected response extraction (for example `children` in `DeviceClient`).
- Failure behavior when expected response keys are missing.

Value:

- Fast tests that catch endpoint typos and payload shape drift early.

### HV8: Site placeholder behavior

Targets:

- `src/roak_sdk/semantics/site.py`

Add tests for one of:

- Current placeholder contract (documented no-op), or
- Implemented behavior once `get_sites()` is defined.

Value:

- Prevents accidental API confusion for Site-specific flows.
