import unittest
from unittest.mock import Mock
from roak_sdk.semantics.project import Project


class TestProject(unittest.TestCase):
    """Unit tests for the Project class."""

    def setUp(self):
        """Set up a mock client and a Project instance for testing."""
        self.mock_client = Mock()
        self.mock_client.headers = {"Authorization": "Bearer abc"}

        # Mock fetch_feeds to return an empty dict to satisfy auto-feed loading
        self.mock_client.fetch_feeds = Mock(return_value={})

        self.project_data = {
            "guid": "guid-123",
            "name": "TestProject",
        }

        self.project = Project(self.project_data, client=self.mock_client)

    def test_initialization(self):
        """Project initializes with correct guid, name, and client."""
        self.assertEqual(self.project.guid, "guid-123")
        self.assertEqual(self.project.name, "TestProject")
        self.assertEqual(self.project.client, self.mock_client)

    def test_client_missing_headers_raises(self):
        """Project should raise ValueError if client has no headers."""
        bad_client = Mock()
        bad_client.headers = None
        bad_client.fetch_feeds = Mock(return_value={})

        with self.assertRaises(ValueError):
            Project(self.project_data, bad_client)

    def test_add_and_get_sites(self):
        """Project correctly stores sites."""
        site1 = Mock()
        site2 = Mock()

        self.project.add_site(site1)
        self.project.add_site(site2)

        self.assertEqual(self.project.get_sites(), [site1, site2])

    def test_repr(self):
        """__repr__ should return readable project identifier."""
        r = repr(self.project)
        self.assertIn("TestProject", r)
        self.assertIn("guid-123", r)
