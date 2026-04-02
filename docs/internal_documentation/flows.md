User calls: project.get_wells()
                ↓
         BaseClient._request()
                ↓
         API returns 401 (token expired)
                ↓
         registry.refresh_tokens()
                ↓
         Roak._refresh_tokens() callback
                ↓
         Auth.refresh_access_token()
                ↓
         Updates headers in all clients
                ↓
         Retry original request
                ↓
         Success (or fail if still 401)