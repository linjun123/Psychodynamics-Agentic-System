from pydantic import BaseModel, ConfigDict


class StrictSchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
