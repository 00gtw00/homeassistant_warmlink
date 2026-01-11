from __future__ import annotations

import hashlib
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    API_TIMEOUT,
    DEFAULT_APP_ID,
    DEFAULT_AREA_CODE,
    DEFAULT_LANG,
    DEFAULT_LOGIN_SOURCE,
    DEFAULT_TYPE,
)


def _md5_hex(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def _extract_token(data: Any) -> str | None:
    if not isinstance(data, dict):
        return None
    obj = data.get("objectResult")
    if isinstance(obj, dict):
        for key in ("x-token", "xToken", "token", "x_token"):
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    for key in ("x-token", "xToken", "token"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


class WarmlinkApi:
    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        base: str,
        lang: str = DEFAULT_LANG,
        login_source: str = DEFAULT_LOGIN_SOURCE,
        area_code: str = DEFAULT_AREA_CODE,
        app_id: str = DEFAULT_APP_ID,
        typ: str = DEFAULT_TYPE,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._base = base.rstrip("/")
        self._lang = lang
        self._login_source = login_source
        self._area_code = area_code
        self._app_id = app_id
        self._type = typ
        self._token: str | None = None

    @property
    def token(self) -> str | None:
        return self._token

    async def _request_json(
        self, method: str, url: str, headers: dict[str, str], json_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                json=json_data,
                timeout=API_TIMEOUT,
            ) as resp:
                return await resp.json(content_type=None)
        except (ClientError, ValueError):
            return {}

    async def login(self) -> str | None:
        url = f"{self._base}/user/login?lang={self._lang}"
        for mode in ("plain", "md5", "md5md5"):
            if mode == "plain":
                password = self._password
            elif mode == "md5":
                password = _md5_hex(self._password)
            else:
                password = _md5_hex(_md5_hex(self._password))
            payload = {
                "password": password,
                "loginSource": self._login_source,
                "areaCode": self._area_code,
                "appId": self._app_id,
                "type": self._type,
                "userName": self._username,
            }
            data = await self._request_json(
                "POST", url, {"Content-Type": "application/json"}, payload
            )
            token = _extract_token(data)
            if token:
                self._token = token
                return token
        return None

    async def device_list(self) -> list[dict[str, Any]]:
        if not self._token:
            return []
        url = f"{self._base}/device/deviceList"
        data = await self._request_json(
            "POST",
            url,
            {"Content-Type": "application/json", "x-token": self._token},
            {},
        )
        obj = data.get("objectResult")
        if isinstance(obj, list):
            return [x for x in obj if isinstance(x, dict)]
        return []

    async def get_device_status(self, device_code: str) -> dict[str, Any]:
        if not self._token:
            return {}
        url = f"{self._base}/device/getDeviceStatus?lang={self._lang}"
        payload = {"appId": self._app_id, "deviceCode": device_code}
        data = await self._request_json(
            "POST",
            url,
            {"Content-Type": "application/json", "x-token": self._token},
            payload,
        )
        obj = data.get("objectResult")
        return obj if isinstance(obj, dict) else {}

    async def get_data_by_code(self, device_code: str, codes: list[str]) -> dict[str, Any]:
        if not self._token:
            return {}
        url = f"{self._base}/device/getDataByCode?lang={self._lang}"
        payload = {"deviceCode": device_code, "appId": self._app_id, "protocalCodes": codes}
        data = await self._request_json(
            "POST",
            url,
            {"Content-Type": "application/json", "x-token": self._token},
            payload,
        )
        obj = data.get("objectResult")
        if isinstance(obj, list):
            result: dict[str, Any] = {}
            for item in obj:
                if not isinstance(item, dict):
                    continue
                code = item.get("code")
                value = item.get("value")
                if isinstance(code, str) and code:
                    result[code] = value
            return result
        return {}

    async def control(self, device_code: str, protocol_code: str, value: str) -> bool:
        if not self._token:
            return False
        url = f"{self._base}/device/control?lang={self._lang}"
        payload = {
            "appId": self._app_id,
            "param": [{"deviceCode": device_code, "protocolCode": protocol_code, "value": value}],
        }
        data = await self._request_json(
            "POST",
            url,
            {"Content-Type": "application/json", "x-token": self._token},
            payload,
        )
        return bool(data)
