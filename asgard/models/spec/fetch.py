from asgard.models.base import BaseModel


class FetchURISpec(BaseModel):
    uri: str
    extract: bool = True
    executable: bool = False
    cache: bool = False
