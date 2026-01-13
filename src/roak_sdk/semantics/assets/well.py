from roak_sdk.semantics.asset import Asset


class Well(Asset):
    STANDARD_FEEDS = [
        "waterLevelReference",
        "diverPressure",
        "wellLength",
        "baroTemperature",
    ]

    def __init__(self, guid: str, name: str, client, project=None):
        super().__init__(guid, name, client, project=project)
        self.name = name
