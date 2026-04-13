ROAK SDK Documentation
======================

The ROAK SDK provides a Python interface for interacting with the ROAK API.

Current release status: **Beta (v0.1.0)**.

Quick Start
-----------

.. code-block:: python

   from roak_sdk import Roak

   roak = Roak(username="your_username", password="your_password")

   # Get all projects
   projects = roak.get_projects()

   # Get wells within a project
   wells = projects[0].get_wells()

   # Get data from a well
   data = wells[0].get_data()

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/roak
   api/project
   api/site
   api/well
   api/borehole
   api/rig
   api/modem
   api/errors
