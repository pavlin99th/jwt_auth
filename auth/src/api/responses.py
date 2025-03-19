from typing import Any

from fastapi import status

from schemas.entity import Detail

err_model: dict[str, type[Detail]] = {"model": Detail}

err_token: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: err_model,
    status.HTTP_422_UNPROCESSABLE_ENTITY: err_model,
}
