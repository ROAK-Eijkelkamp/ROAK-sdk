from roak_sdk.clients.base_client import BaseClient


class ProjectClient(BaseClient):
    """Handles project endpoints."""

    def get_project(self, name=None):
        """Fetch projects. Returns all if name is None, otherwise the one with matching name."""
        url = f"{self.base_url}/api/ed/projects"
        projects = self._request(url)

        if name is None:
            return projects  # return list of all projects

        # search for project with matching name
        for project in projects:
            if project["name"] == name:
                return project

        raise ValueError(f"Project '{name}' not found.")

    def get_project_data(self, name=None):
        """Fetch project dict(s) from API"""
        url = f"{self.base_url}/api/ed/projects"
        projects = self._request(url)

        if name is None:
            return projects

        for project in projects:
            if project["name"] == name:
                return project

        raise ValueError(f"Project '{name}' not found.")

    def fetch_feeds(self, project_guid: str) -> dict:
        """
        Fetch feed data for the given asset or project GUID.

        This default implementation returns an empty dict to prevent crashes
        for clients that don’t support feeds. The `guid` parameter is required
        to match the method signature and is used by other implementations.

        Args:
            guid (str): The unique identifier (GUID) of the asset or project.

        Returns:
            dict: Feed data. Empty dict in this default implementation.
        """
        try:
            url = f"{self.base_url}/api/ed/projects/{project_guid}/feeds"
            response = self._request(url)
            if not isinstance(response, dict):
                print(
                    f"WARNING: fetch_feeds() expected dict, got {type(response).__name__}. Returning empty dict."
                )
                return {}
            return response
        except Exception as e:
            print(f"Failed to fetch feeds for project '{project_guid}': {e}")
            return {}
