# ROAK SDK: ROAK vs Project Gap Analysis

**Date:** April 2, 2026

## Executive Summary

This document compares the public method surfaces of the `Roak` facade and the `Project` semantic container.

The main finding is that the SDK currently exposes **two different navigation models**:

- **`Roak`** is strong at account-wide typed lookups (`Project`, `Site`, `Rig`, `Modem`, `Customer`)
- **`Project`** is strong at scoped asset navigation (`Asset`, `Well`, `Borehole`)

That split is understandable at a high level, but the public API is currently less symmetric than users would reasonably expect:

- `Project` still has the stronger public generic list pattern via `get_assets()`
- `Roak` now covers the high-confidence account-wide lookup gaps for assets, wells, and boreholes
- `Roak` has rig/site/modem lookup patterns that `Project` does not mirror within scope
- Repository documentation still describes older or more symmetric method patterns that are not present in code

The strongest remaining gaps are now mostly the still-missing generic `Roak.get_assets()` list method and the project-scoped rig/modem methods.

---

## Surface Comparison

| Pattern | `Roak` | `Project` | Notes |
|---------|--------|-----------|-------|
| Generic list method | ~~`get_assets()`~~ ❌ | `get_assets()` | `Project` supports generic scoped assets; `Roak` does not expose a generic account-wide asset list. |
| Generic lookup by GUID | Complete | `get_asset_by_guid()` | `Roak` now exposes account-wide generic lookup via the semantic factory. |
| Generic lookup by name | Complete | `get_asset_by_name()` | `Roak` now exposes account-wide generic name lookup with optional type filtering. |
| Wells: list + by name + by GUID | Complete | Complete | Both classes now provide the full well triad. |
| Boreholes: list + by name + by GUID | Complete | Complete | Both classes now provide the full borehole triad. |
| Rigs: list + by name + by GUID | Complete | ~~Missing~~ ❌ | `Roak` has a full rig triad; `Project` has no scoped rig convenience methods. |
| Modems: list + by name + by GUID | Complete | ~~Missing~~ ❌ | `Roak` has a full modem triad; `Project` has no scoped modem convenience methods. |
| Sites: list + by name + by GUID | Complete | ~~Missing~~ ❌ | `Roak` has a full site triad; `Project` has no scoped site convenience methods. |
| Projects: list + by name + by GUID | Complete | Not applicable | `Project` is itself the scoped project object. |
| Customers: list + by name + by GUID | Complete | Not applicable | `Project` should not mirror customer-root operations. |

---

## 1. Roak Class - Missing Account-Wide Asset Methods

The `Project` class exposes a clear and ergonomic asset pattern:

- `get_assets()`
- `get_asset_by_guid()`
- `get_asset_by_name()`
- `get_wells()`, `get_well_by_guid()`, `get_well_by_name()`
- `get_boreholes()`, `get_borehole_by_guid()`, `get_borehole_by_name()`

At the top level, `Roak` now exposes the same lookup pattern for single assets and typed well/borehole access. The main remaining asymmetry is on generic list retrieval.

Users still cannot do the direct list equivalent of:

1. `roak.get_assets()`
2. `roak.get_assets(asset_type="...")`

So the account-wide lookup gap is mostly resolved, but the account-wide list shape is still incomplete.

### High-Confidence Missing Methods

These methods were the strongest original gaps and are now implemented.

| Status | Method Name | Location | Signature | Rationale |
|--------|-------------|----------|-----------|-----------|
| [x] | **get_asset_by_guid** | `Roak` class | `get_asset_by_guid(guid: str) -> Asset` | `RoakClient.get_asset_by_guid()` already exists. The facade is the missing piece. |
| [x] | **get_asset_by_name** | `Roak` class | `get_asset_by_name(name: str, asset_type: str \| None = None, allow_first_match: bool = False) -> Asset` | `RoakClient.get_asset_by_name_and_type()` already supports the lookup pattern. |
| [x] | **get_well_by_guid** | `Roak` class | `get_well_by_guid(guid: str) -> Well` | Mirrors `Project.get_well_by_guid()` for account-wide access. |
| [x] | **get_well_by_name** | `Roak` class | `get_well_by_name(name: str, allow_first_match: bool = False) -> Well` | Removes forced project hopping for exact-name well lookup. |
| [x] | **get_borehole_by_guid** | `Roak` class | `get_borehole_by_guid(guid: str) -> Borehole` | Mirrors `Project.get_borehole_by_guid()` for account-wide access. |
| [x] | **get_borehole_by_name** | `Roak` class | `get_borehole_by_name(name: str, allow_first_match: bool = False) -> Borehole` | Removes forced project or rig traversal for borehole lookup. |

### Medium-Confidence Missing Methods

These are still the relevant remaining account-wide list questions.

| Status | Method Name | Location | Signature | Rationale |
|--------|-------------|----------|-----------|-----------|
| [ ] | **get_assets** | `Roak` class | `get_assets(asset_type: str \| None = None) -> list[Asset]` | Useful generic entry point, but requires a clear account-wide listing rule. |
| [x] | **get_wells** | `Roak` class | `get_wells() -> list[Well]` | Would mirror `Project.get_wells()` at facade level. |
| [x] | **get_boreholes** | `Roak` class | `get_boreholes() -> list[Borehole]` | Would mirror `Project.get_boreholes()` at facade level. |

### Rationale

The strongest remaining argument here is consistency. Right now:

- `Roak` is already the public entry point
- `RoakClient` already has generic lookup capabilities and a generic account-wide `get_assets(type_guid=...)` helper
- users can already fetch typed top-level objects like `Rig`, `Site`, and `Modem`
- `Roak` now has a private `_get_assets(...)` helper used by `get_sites()`, `get_wells()`, and `get_boreholes()`

Given that, the remaining omission is specifically the lack of a public generic list method on `Roak`, not the lack of asset lookups in general.

### Implementation Notes

- `get_asset_by_guid()` now delegates directly to `RoakClient.get_asset_by_guid()` and passes the result through `make_asset()`.
- `get_asset_by_name()` now delegates to `RoakClient.get_asset_by_name_and_type()` and passes the result through `make_asset()`.
- `get_wells()` and `get_boreholes()` are now routed through a shared private `Roak._get_assets(...)` helper.
- A future public `Roak.get_assets()` can likely be layered over the same client/helper path if the account-wide list semantics are finalized.

---

## 2. Project Class - Missing Scoped Parity for Site and Device Types

The asymmetry also goes in the other direction. `Roak` exposes strong typed lookup patterns for:

- `Site`
- `Rig`
- `Modem`

But `Project` does not offer matching scoped convenience methods for those same entity types.

### Strong Candidate: Project/Scope Site Methods

This is the strongest `Project`-side gap because the surrounding code already implies that site scoping is part of the intended model.

Evidence:

- `Site` inherits from `Project`
- `Customer` inherits from `Project`
- `Site.get_sites()` exists specifically to block nested sites with a `NotImplementedError`

That last point only makes architectural sense if `get_sites()` is expected to exist on the broader `Project` or `Customer` surface.

| Status | Method Name | Location | Signature | Rationale |
|--------|-------------|----------|-----------|-----------|
| [x] | **get_sites** | `Project` class | `get_sites() -> list[Site]` | Lets `Project` and especially `Customer` enumerate child sites. |
| [x] | **get_site_by_guid** | `Project` class | `get_site_by_guid(guid: str) -> Site` | Scoped lookup symmetry with `Roak.get_site_by_guid()`. |
| [x] | **get_site_by_name** | `Project` class | `get_site_by_name(name: str, allow_first_match: bool = False) -> Site` | Scoped lookup symmetry with `Roak.get_site_by_name()`. |

### Probable Candidate: Project-Scoped Rig Methods

This is also a credible gap, but it is one step less certain than sites.

Evidence:

- `Roak` has a complete rig triad
- `ProjectClient.get_assets()` accepts arbitrary `typeGuid` filters
- [docs/architecture.md](architecture.md) still describes a Project-level rig method (`get_all_rigs()`), even though it is not implemented in code

| Status | Method Name | Location | Signature | Rationale |
|--------|-------------|----------|-----------|-----------|
| [ ] | **get_rigs** | `Project` class | `get_rigs() -> list[Rig]` | Natural scoped equivalent of `Roak.get_rigs()`. |
| [ ] | **get_rig_by_guid** | `Project` class | `get_rig_by_guid(guid: str) -> Rig` | Scoped lookup symmetry. |
| [ ] | **get_rig_by_name** | `Project` class | `get_rig_by_name(name: str, allow_first_match: bool = False) -> Rig` | Scoped lookup symmetry. |

### Low-Confidence Candidate: Project-Scoped Modem Methods

These methods are plausible, but there is less evidence that modem objects are expected to participate in project-scoped navigation.

| Status | Method Name | Location | Signature | Rationale |
|--------|-------------|----------|-----------|-----------|
| [ ] | **get_modems** | `Project` class | `get_modems() -> list[Modem]` | Could be useful if project scope includes modem assets. |
| [ ] | **get_modem_by_guid** | `Project` class | `get_modem_by_guid(guid: str) -> Modem` | Scoped modem lookup, if supported by API scope. |
| [ ] | **get_modem_by_name** | `Project` class | `get_modem_by_name(name: str, allow_first_match: bool = False) -> Modem` | Scoped modem name lookup, if supported by API scope. |

### Important Constraint

These `Project`-side additions are not just facade work.

Current runtime limitations:

- `make_asset()` only materializes `Well`, `Borehole`, and generic `Asset`
- `Project.get_assets()` filters results to `ASSET_TYPES`, which currently only includes wells and boreholes

So even if the API already supports scoped rig/site/modem listing, the semantic layer would still need to be widened before the methods feel consistent and type-safe.

---

## 3. Documentation Drift Indicates Intended Symmetry

Several docs still describe a more symmetric or older method surface than the code actually provides.

### Drift Observed

- [docs/architecture.md](architecture.md) documents `Roak.get_all_projects()` and `Project.get_all_wells()`, `Project.get_all_boreholes()`, `Project.get_all_rigs()`
- [docs/flows.md](flows.md) still shows `project.get_all_wells()` in the token refresh flow
- [docs/missing_methods_analysis.md](missing_methods_analysis.md) discusses `Site.get_sites()` as if `Project.get_sites()` already existed higher in the hierarchy

### Why This Matters

This drift is useful evidence because it suggests the SDK design previously aimed for:

- stronger parity between top-level and scoped navigation
- a broader `Project` container role than the current code implements
- older `get_all_*` naming that has since been simplified to `get_*`

That does not prove every missing method should be added, but it does make the current asymmetry look more like unfinished convergence than deliberate minimalism.

---

## 4. Recommended Priority

### High Priority

- [x] `Roak.get_asset_by_guid()`
- [x] `Roak.get_asset_by_name()`
- [x] `Roak.get_well_by_guid()`
- [x] `Roak.get_well_by_name()`
- [x] `Roak.get_borehole_by_guid()`
- [x] `Roak.get_borehole_by_name()`
- [x] `Project.get_sites()`
- [x] `Project.get_site_by_guid()`
- [x] `Project.get_site_by_name()`

### Medium Priority

- [ ] `Roak.get_assets()`
- [x] `Roak.get_wells()`
- [x] `Roak.get_boreholes()`
- [ ] `Project.get_rigs()`
- [ ] `Project.get_rig_by_guid()`
- [ ] `Project.get_rig_by_name()`

### Low Priority

- [ ] `Project.get_modems()`
- [ ] `Project.get_modem_by_guid()`
- [ ] `Project.get_modem_by_name()`

---

## Testing Recommendations

When implementing any of the above methods, test for:

1. **Surface symmetry**: list, lookup-by-name, and lookup-by-GUID should behave consistently across `Roak` and `Project`.
2. **Type validation**: typed convenience methods should raise `AssetTypeMismatchError` when the returned asset is not of the expected semantic type.
3. **Allow-first-match behavior**: name-based methods should preserve the existing ambiguity rules already used in `RoakClient` and `ProjectClient`.
4. **Factory coverage**: if `Project` grows rig/site/modem support, `make_asset()` and related tests need to recognize those semantic types.
5. **Documentation updates**: the architecture and flow docs should be corrected once the intended surface is finalized.

---

## References

- [src/roak_sdk/roak.py](../src/roak_sdk/roak.py)
- [src/roak_sdk/semantics/project.py](../src/roak_sdk/semantics/project.py)
- [src/roak_sdk/clients/roak_client.py](../src/roak_sdk/clients/roak_client.py)
- [src/roak_sdk/clients/project_client.py](../src/roak_sdk/clients/project_client.py)
- [src/roak_sdk/semantics/factory.py](../src/roak_sdk/semantics/factory.py)
- [src/roak_sdk/semantics/site.py](../src/roak_sdk/semantics/site.py)
- [src/roak_sdk/semantics/customer.py](../src/roak_sdk/semantics/customer.py)
- [docs/architecture.md](architecture.md)
- [docs/flows.md](flows.md)
- [docs/missing_methods_analysis.md](missing_methods_analysis.md)