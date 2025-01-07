"""Sample API Client."""

from __future__ import annotations

import base64
import socket
from typing import Any

import aiohttp
import async_timeout
from homeassistant.util.json import json_loads

from .const import LOGGER


class PowerOceanApiClientError(Exception):
    """Exception to indicate a general API error."""


class PowerOceanApiClientCommunicationError(
    PowerOceanApiClientError,
):
    """Exception to indicate a communication error."""


class PowerOceanApiClientAuthenticationError(
    PowerOceanApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise PowerOceanApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class PowerOceanApiClient:
    """Sample API Client."""

    def __init__(
        self,
        serial: str,
        email: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self.serial = serial
        self._email = email
        self._password = password
        self._session = session
        self._url_auth = "https://api.ecoflow.com/auth/login"
        self._url_fetch_data = f"https://api-e.ecoflow.com/provider-service/user/device/detail?sn={self.serial}"
        self._token = None

    async def async_authorize(self) -> Any:
        """Authorize the user."""
        headers = {"lang": "en_US", "content-type": "application/json"}
        data = {
            "email": self._email,
            "password": base64.b64encode(self._password.encode()).decode(),
            "scene": "EP_ADMIN",
            "userType": "ECOFLOW",
        }
        response = self._api_wrapper(
            method="post",
            url=self._url_auth,
            data=data,
            headers=headers,
        )
        response = await response
        self.token = response["data"]["token"]  # type: ignore  # noqa: PGH003

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
            # url=self._url_fetch_data,
            # headers={"authorization": f"Bearer {self._token}"},
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise PowerOceanApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise PowerOceanApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise PowerOceanApiClientError(
                msg,
            ) from exception
