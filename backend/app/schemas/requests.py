from typing import Annotated
from pydantic import Field

Snr = Annotated[float, Field(ge=-15, le=40, allow_inf_nan=False)]
