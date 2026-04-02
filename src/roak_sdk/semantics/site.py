from .project import Project

class Site(Project):
    """
    Represents a Site within a project.

    Basically provides all the same functionality as Project, except the possibility to get the sites.
    """
    
    def get_sites(self):
        """
        Override to prevent hierarchical site nesting.
        
        Raises:
            NotImplementedError: Sites do not support containing child sites.
        """
        raise NotImplementedError("Sites cannot contain child sites. Site nesting is not supported.")