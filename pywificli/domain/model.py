"""Common domain models"""

from dataclasses import dataclass


@dataclass
class BaseModel:
    """The base model"""

    a: str


@dataclass
class Model(BaseModel):
    """A derived model"""

    b: int
