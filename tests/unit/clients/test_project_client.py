import unittest
from unittest.mock import patch, Mock
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.auth import DEFAULT_URL


class TestProjectClient(unittest.TestCase):
    """Unit tests for ProjectClient."""

    @patch.object(ProjectClient, "_request")
    def test_get_project_returns_all(self, mock_request):
        """Test get_project returns a list of all projects when no name is specified."""
        mock_request.return_value = [{"name": "Proj1"}, {"name": "Proj2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake-token"})
        projects = client.get_project()
        self.assertEqual(len(projects), 2)

    @patch.object(ProjectClient, "_request")
    def test_get_project_by_name(self, mock_request):
        """Test get_project returns the correct project dict when a valid name is provided."""
        mock_request.return_value = [{"name": "Proj1"}, {"name": "Proj2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake-token"})
        proj = client.get_project("Proj2")
        self.assertEqual(proj["name"], "Proj2")

    @patch.object(ProjectClient, "_request")
    def test_get_project_name_not_found_raises(self, mock_request):
        """Test get_project raises ValueError if the specified project name is not found."""
        mock_request.return_value = [{"name": "Proj1"}, {"name": "Proj2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake-token"})
        with self.assertRaises(ValueError):
            client.get_project("Proj3")

    @patch.object(ProjectClient, "_request")
    def test_get_project_data_returns_all(self, mock_request):
        """Test get_project_data returns all projects when no name is specified."""
        mock_request.return_value = [{"name": "P1"}, {"name": "P2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake"})
        projects = client.get_project_data()
        self.assertEqual(len(projects), 2)

    @patch.object(ProjectClient, "_request")
    def test_get_project_data_by_name(self, mock_request):
        """Test get_project_data returns a single project dict when name exists."""
        mock_request.return_value = [{"name": "P1"}, {"name": "P2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake"})
        project = client.get_project_data("P2")
        self.assertEqual(project["name"], "P2")

    @patch.object(ProjectClient, "_request")
    def test_get_project_data_name_not_found_raises(self, mock_request):
        """Test get_project_data raises ValueError when project name does not exist."""
        mock_request.return_value = [{"name": "P1"}, {"name": "P2"}]
        client = ProjectClient(authorization={"Authorization": "Bearer fake"})
        with self.assertRaises(ValueError):
            client.get_project_data("P3")
