# ROAK SDK: Missing Methods Analysis

**Date:** March 31, 2026

## Executive Summary

This document identifies methods that are likely missing from the ROAK SDK based on consistent patterns found across similar classes. The analysis covers:

- **Consistency gaps**: Methods that exist for one type but not others
- **Pattern asymmetries**: Lookups (by name, by GUID) implemented inconsistently
- **Asset hierarchy mismatches**: Methods available on one asset type but missing on similar types

---

## Implementation Status

**Overall Progress**: 5 of 10 items completed

| Category | Total | Completed | Remaining |
|----------|-------|-----------|-----------||
| High Priority | 4 | 4 | 0 |
| Medium Priority | 2 | 1 | 1 |
| Low Priority | 3 | 0 | 3 |
| **TOTAL** | **10** | **5** | **5** |

---

## 1. Roak Class - Lookup Method Inconsistencies

The `Roak` class (main entry point) provides lookup methods for different entity types. The pattern is inconsistent:

### Pattern Observed
- **Customers**: `get_customers()`, `get_customer_by_name()`, `get_customer_by_guid()`
- **Projects**: `get_projects()`, `get_project_by_name()`, `get_project_by_guid()`
- **Sites**: `get_sites()`, `get_site_by_name()`, ~~`get_site_by_guid()`~~ ❌ MISSING
- **Rigs**: `get_rigs()`, `get_rig_by_name()`, ~~`get_rig_by_guid()`~~ ❌ MISSING
- **Modems**: `get_modems()`, ~~`get_modem_by_name()`~~ ❌ MISSING, `get_modem_by_guid()`

### Missing Methods

| Status | Method Name | Location | Signature | Purpose | 
|--------|-------------|----------|-----------|---------|
| [x] | **get_site_by_guid** | `Roak` class | `get_site_by_guid(guid: str) -> Site` | Fetch a site by its GUID. Currently only `get_site_by_name()` is available. |
| [x] | **get_rig_by_guid** | `Roak` class | `get_rig_by_guid(guid: str) -> Rig` | Fetch a rig by its GUID. Currently only `get_rig_by_name()` is available. |
| [x] | **get_modem_by_name** | `Roak` class | `get_modem_by_name(name: str, allow_first_match: bool = False) -> Modem` | Fetch a modem by its name. Currently only `get_modem_by_guid()` is available. |

### Rationale
These methods complete the lookup pattern: for every entity type that can be listed (`get_*s()`), users should be able to fetch by both name and GUID. This provides consistent, predictable access patterns across the SDK interface.

---

## 2. Rig Class - Borehole Lookup Methods

The `Rig` class can retrieve boreholes, but lookup is incomplete:

### Pattern Observed
- **Current methods**: `get_boreholes()`, `get_borehole_by_name()`
- **Missing method**: ~~`get_borehole_by_guid()`~~ ❌ MISSING

### Missing Methods

| Status | Method Name | Location | Signature | Purpose |
|--------|-------------|----------|-----------|---------|
| [x] | **get_borehole_by_guid** | `Rig` class | `get_borehole_by_guid(guid: str) -> Borehole` | Fetch a borehole by its GUID from this rig's boreholes. Complements `get_borehole_by_name()` to provide complete lookup methods. |

### Rationale
The pattern used in `Project` class provides both `get_borehole_by_guid()` and `get_borehole_by_name()`. The `Rig` class should have the same symmetry since rigs also contain boreholes. 

**Implementation approach**: Similar to `Project.get_borehole_by_guid()`, it should:
1. Call `get_boreholes()`
2. Find the matching borehole by GUID
3. Raise `ValueError` if not found

---

## 3. Project/Site Class - Asset Retrieval Completeness

The `Project` class provides complete asset methods for Wells and Boreholes. However, the parent hierarchy might be incomplete:

### Current Status
- **Complete**: Wells have `get_wells()`, `get_well_by_guid()`, `get_well_by_name()`
- **Complete**: Boreholes have `get_boreholes()`, `get_borehole_by_guid()`, `get_borehole_by_name()`

### Note on Site Class
The `Site` class (file: [src/roak_sdk/semantics/site.py](../src/roak_sdk/semantics/site.py)) extends `Project` and currently overrides `get_sites()`:
```python
def get_sites(self):
    pass
```

**Context**: Sites cannot contain child sites (hierarchical). Since `Site` inherits from `Project`, it automatically inherits the `get_sites()` method. The stub override explicitly prevents access to this method on Site objects.

**Recommendation**: Replace the silent `pass` with an explicit error to clarify intent:
```python
def get_sites(self):
    """Sites cannot contain child sites."""
    raise NotImplementedError("Sites do not support hierarchical nesting. A Site cannot contain other Sites.")
```

This makes the limitation explicit to users rather than silently returning nothing.

---

## 4. Device Class - Child Device Filtering

The `Device` class provides a generic `get_children()` method but lacks filtering capabilities:

### Pattern Observed
- **Current method**: `get_children() -> list[Device]` (returns all children)
- **Missing convenience methods**: 
  - ~~`get_children_by_name()`~~ ❌ MISSING
  - ~~`get_child_by_name()`~~ potentially useful

### Analysis
Since `Device` is the base for both `Rig` and `Modem`:
- **Rig** has specific methods: `get_boreholes()`, `get_borehole_by_name()`
- **Modem** has: `get_data_through_children()` but no filtering

### Potential Missing Methods

| Status | Method Name | Location | Signature | Purpose |
|--------|-------------|----------|-----------|---------|
| [ ] | **get_children_by_name** | `Device` class | `get_children_by_name(name: str, allow_first_match: bool = False) -> list[Device]` | Fetch child devices by name. Provides a generic filtering mechanism that could be used by Modem or other device types. |

### Rationale
Some device types might have multiple children with the same type. A generic filtering method on `Device` would provide a reusable pattern.

---

## 5. Modem Class - Specific Child Retrieval

The `Modem` class has `get_data_through_children()` but might benefit from more specific asset retrieval:

### Current Status
- Has: `get_data_through_children()` (aggregate data from all children)
- Missing: Direct access methods for specific child types

### Potential Missing Methods

| Status | Method Name | Location | Signature | Purpose |
|--------|-------------|----------|-----------|---------|
| [ ] | **get_wells** | `Modem` class | `get_wells() -> list[Well]` | Get all child wells (if applicable). Filters `get_children()` to return only Well-type children. |
| [ ] | **get_boreholes** | `Modem` class | `get_boreholes() -> list[Borehole]` | Get all child boreholes (if applicable). Filters `get_children()` to return only Borehole-type children. |
| [ ] | **get_rigs** | `Modem` class | `get_rigs() -> list[Rig]` | Get all child rigs (if applicable). Filters `get_children()` to return only Rig-type children. |

### Rationale
If a Modem can have Wells, Boreholes, or Rigs as children (which may be the case in multi-level hierarchies), having convenience methods would improve usability comparable to the methods available on `Rig` and `Project`.

**Decision needed**: Clarify whether:
1. Modems can have wells/boreholes/rigs as children
2. If so, implement these convenience methods
3. If not, document this limitation clearly

---

## 6. Class Hierarchy Summary

```
Semantic (base)
├── Asset
│   ├── Well
│   ├── Borehole
│   └── (generic Asset)
├── Device (extends Asset)
│   ├── Rig
│   └── Modem
├── Project
│   ├── Site
│   └── Customer
```

**Pattern Note**: All container types (Project, Site, Customer) should provide three access methods per asset type:
1. `get_<asset_type_plural>()`
2. `get_<asset_type_singular>_by_name()`
3. `get_<asset_type_singular>_by_guid()`

---

## Implementation Priority

### High Priority (Complete the API patterns)
- [x] `Roak.get_site_by_guid()` - Completes Site lookup consistency
- [x] `Roak.get_rig_by_guid()` - Completes Rig lookup consistency  
- [x] `Roak.get_modem_by_name()` - Completes Modem lookup consistency
- [x] `Rig.get_borehole_by_guid()` - Completes Borehole lookup within Rig

### Medium Priority (Clarifications needed)
- [x] `Site.get_sites()` - Replace silent `pass` with explicit `NotImplementedError` to clarify that sites cannot nest hierarchically
- [ ] `Device.get_children_by_name()` - Evaluate generic filtering value

### Low Priority (Nice-to-have)
- [ ] `Modem.get_wells()` - Only if hierarchy supports
- [ ] `Modem.get_boreholes()` - Only if hierarchy supports
- [ ] `Modem.get_rigs()` - Only if hierarchy supports

---

## Testing Recommendations

When implementing these methods, ensure:
1. **Consistent error handling**: Match existing error behavior (ValueError for not found, TypeError for wrong types)
2. **Type validation**: Validate that returned objects are of expected type
3. **Pattern coverage**: Test name lookup, GUID lookup, and edge cases (not found, duplicates if `allow_first_match`)
4. **Documentation**: Add docstrings following the same format as existing methods

---

## References

- [Roak class](../src/roak_sdk/roak.py)
- [Project class](../src/roak_sdk/semantics/project.py)
- [Rig class](../src/roak_sdk/semantics/devices/rig.py)
- [Modem class](../src/roak_sdk/semantics/devices/modem.py)
- [Device class](../src/roak_sdk/semantics/device.py)
- [Site class](../src/roak_sdk/semantics/site.py)
- [Asset class](../src/roak_sdk/semantics/asset.py)

