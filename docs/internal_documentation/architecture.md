# ROAK SDK Architecture

## Class Diagram

```mermaid
classDiagram
    %% ===== ENTRY POINT =====
    class Roak {
        +Auth auth
        +dict headers
        -ClientRegistry _registry
        -RoakClient _roak_client
        +__init__(username, password, base_url)
        -_refresh_tokens() dict~str,str~
        +refresh_tokens()
        +get_asset_by_guid(guid) Asset
        +get_asset_by_name(name, asset_type, allow_first_match) Asset
        -_get_assets(asset_type, constructor) list
        +get_wells() list~Well~
        +get_boreholes() list~Borehole~
        +get_project_by_name(name) Project
        +get_project_by_guid(guid) Project
        +get_projects() list~Project~
        +get_sites() list~Site~
        +get_site_by_name(name) Site
        +get_site_by_guid(guid) Site
        +get_rigs() list~Rig~
        +get_rig_by_name(name) Rig
        +get_rig_by_guid(guid) Rig
        +get_modems() list~Modem~
        +get_modem_by_guid(guid) Modem
        +get_modem_by_name(name) Modem
    }

    %% ===== CLIENT REGISTRY =====
    class ClientRegistry {
        +dict headers
        +str base_url
        -Callable _refresh_callback
        -dict _clients
        +get(client_class) T
        +update_headers(new_headers)
        +refresh_tokens() dict~str,str~
    }

    %% ===== CLIENTS =====
    class BaseClient {
        +dict headers
        +str base_url
        -ClientRegistry _registry
        +_request(url, params) dict
    }

    class datetime_to_millis {
        <<function>>
        +datetime_to_millis(dt) int
    }
    
    class RoakClient {
        +get_assets(type_guid) list~dict~
        +get_asset_by_guid(guid) dict
        +get_asset_by_name_and_type(name, type_guid, allow_first_match) dict
        +get_wells() list~dict~
        +get_boreholes() list~dict~
        +get_sites() list~dict~
        +get_customers() list~dict~
        +get_projects() list~dict~
        +get_project_by_guid(guid) dict
        +get_rigs() list~dict~
        +get_modems() list~dict~
    }
    
    class ProjectClient {
        +get_assets(project_guid, asset_type) list~dict~
        +get_asset_by_guid(guid) dict
        +get_asset_by_name(project_guid, name, asset_type) dict
    }
    
    class AssetClient {
        +get_data(asset_guid, start_date, end_date, feeds) list~dict~
        +get_feeds(asset_guid) list~dict~
    }

    %% ===== SEMANTICS =====
    class Semantic {
        -dict _data
        +str guid
        +str name
        +__getattr__(name) Any
        +__str__() str
        +__repr__() str
    }
    
    class Project {
        -ClientRegistry _registry
        -ProjectClient _client
        +get_assets(asset_type) list~Asset~
        +get_asset_by_guid(guid) Asset
        +get_asset_by_name(name, asset_type) Asset
        +get_sites() list~Site~
        +get_site_by_guid(guid) Site
        +get_site_by_name(name) Site
        +get_wells() list~Well~
        +get_well_by_guid(guid) Well
        +get_well_by_name(name) Well
        +get_boreholes() list~Borehole~
        +get_borehole_by_guid(guid) Borehole
        +get_borehole_by_name(name) Borehole
    }
    
    class Asset {
        -ClientRegistry _registry
        -AssetClient _client
        +list STANDARD_FEEDS
        +int DEFAULT_TIMEFRAME_DAYS
        +get_data(start_date, end_date, feeds) list~dict~
        +get_feeds() list~dict~
        +get_standard_feeds() list~dict~
    }
    
    class Well {
        +STANDARD_FEEDS = [water_level, ...]
        +DEFAULT_TIMEFRAME_DAYS = 7
    }
    
    class Borehole {
        +STANDARD_FEEDS = [depth, ...]
        +DEFAULT_TIMEFRAME_DAYS = 1
    }
    
    class Rig {
        +STANDARD_FEEDS = [position, ...]
        +DEFAULT_TIMEFRAME_DAYS = 1
    }

    %% ===== FACTORY =====
    class factory {
        <<module>>
        +make_asset(data, registry) Asset
        +ASSET_TYPE_WELL
        +ASSET_TYPE_BOREHOLE
        +ASSET_TYPE_RIG
    }

    %% ===== RELATIONSHIPS =====
    Roak --> ClientRegistry : creates & owns
    Roak --> RoakClient : uses via registry
    Roak --> Project : creates
    Roak ..> ClientRegistry : _refresh_tokens callback
    
    ClientRegistry --> BaseClient : creates & caches
    
    BaseClient <|-- RoakClient
    BaseClient <|-- ProjectClient
    BaseClient <|-- AssetClient
    BaseClient --> ClientRegistry : calls refresh_tokens on 401
    BaseClient ..> datetime_to_millis : uses
    
    Semantic <|-- Project
    Semantic <|-- Asset
    Asset <|-- Well
    Asset <|-- Borehole
    Asset <|-- Rig
    
    Project --> ClientRegistry : holds reference
    Project --> ProjectClient : uses via registry
    Project --> factory : uses make_asset()
    
    Asset --> ClientRegistry : holds reference
    Asset --> AssetClient : uses via registry
    AssetClient ..> datetime_to_millis : uses for from/to params
```

## Token Refresh Flow

```mermaid
sequenceDiagram
    participant Client as BaseClient
    participant Registry as ClientRegistry
    participant Roak
    participant Auth

    Client->>API: GET request
    API-->>Client: 401 Unauthorized
    Client->>Registry: refresh_tokens()
    Registry->>Roak: _refresh_callback()
    Roak->>Auth: refresh_access_token()
    Auth-->>Roak: new headers
    Roak-->>Registry: new headers
    Registry->>Registry: update_headers()
    Registry-->>Client: new headers
    Client->>API: Retry with new headers
    API-->>Client: 200 OK
```

## API Surface Notes

- `Project` remains the public scoped container for generic asset listing via `get_assets()`.
- `Roak` now provides direct account-wide lookup methods for generic assets, wells, and boreholes.
- `Roak.get_sites()`, `Roak.get_wells()`, and `Roak.get_boreholes()` share a private `_get_assets(...)` helper backed by `RoakClient.get_assets(type_guid=...)`.
- `make_asset()` currently materializes `Well`, `Borehole`, and generic `Asset`. It does not yet widen generic account-wide list results into `Site`, `Rig`, or `Modem`.