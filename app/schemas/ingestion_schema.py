from pydantic import BaseModel

class IngestFilePathRequest(BaseModel):
    file_path: str