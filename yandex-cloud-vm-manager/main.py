import logging
import asyncio
import os
from datetime import datetime

from aiohttp import ClientResponse
from dotenv import load_dotenv
import aiohttp


class Cloud:
    id: str
    name: str

    def __init__(self):
        pass

    def from_dict(self, data: dict):
        self.id = data['id']
        self.name = data['name']
        return self


class Folder:
    id: str
    name: str
    cloud_id: str

    def __init__(self):
        pass

    def from_dict(self, data: dict):
        self.id = data['id']
        self.cloud_id = data['cloudId']
        self.name = data['name']
        return self


class Instance:
    id: str
    folder_id: str
    labels: dict[str, str] | None

    def __init__(self):
        pass

    def from_dict(self, data: dict):
        self.id = data['id']
        self.folder_id = data['folderId']
        self.labels = data['labels'] if 'labels' in data else {}
        return self


class YandexCloudAPI:
    oauth_token: str
    iam_token: str
    _cloud_host_base = "api.cloud.yandex.net"
    _iam_host = f"https://iam.{_cloud_host_base}"
    _compute_host = f"https://compute.{_cloud_host_base}"
    _resource_manager_host = f"https://resource-manager.{_cloud_host_base}"
    _logger: logging.Logger
    _token_lock = asyncio.Lock()

    def __init__(self, oauth_token: str):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.oauth_token = oauth_token
        if not self.oauth_token:
            raise ValueError("OAuth token is required")

    async def update_iam_token(self) -> None:
        async with self._token_lock:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(f"{self._iam_host}/iam/v1/tokens",
                                            json={"yandexPassportOauthToken": self.oauth_token}) as response:
                        if response.status != 200:
                            self._logger.error(f"Error updating IAM token: {response.status} {await response.text()}")
                        else:
                            data = await response.json()
                            self.iam_token = data["iamToken"]
                            self._logger.info("IAM token successfully updated")
                except aiohttp.ClientError as e:
                    self._logger.error(f"HTTP error occurred: {e}")

    async def _post_authorized(self, url: str, data: dict) -> ClientResponse:
        async with self._token_lock:
            token = self.iam_token
        session = aiohttp.ClientSession()
        response = await session.post(url=url, data=data,
                                      headers={"Authorization": f"Bearer {token}"})
        await session.close()
        return response

    async def _get_authorized(self, url: str, params: dict) -> ClientResponse:
        async with self._token_lock:
            token = self.iam_token
        session = aiohttp.ClientSession()
        response = await session.get(url=url, params=params,
                                     headers={"Authorization": f"Bearer {token}"})
        await session.close()
        return response

    async def get_cloud_list(self) -> list[Cloud]:
        response = await self._get_authorized(f"{self._resource_manager_host}/resource-manager/v1/clouds", {})
        if response.status != 200:
            error = (await response.json())["message"]
            self._logger.error(f"Error getting cloud list: {error}")
            return []
        res = await response.json()
        if res:
            clouds = res["clouds"]
            clouds = [Cloud().from_dict(item) for item in clouds]
            return clouds
        else:
            return []

    async def get_folders_in_cloud(self, cloud_id: str) -> list[Folder]:
        response = await self._get_authorized(f"{self._resource_manager_host}/resource-manager/v1/folders",
                                              {"cloudId": cloud_id})
        if response.status != 200:
            error = (await response.json())["message"]
            self._logger.error(f"Error getting folders list: {error}")
            return []
        res = await response.json()
        if res:
            folders = res["folders"]
            folders = [Folder().from_dict(item) for item in folders]
            return folders
        else:
            return []

    async def get_vms_in_folder(self, folder_id: str) -> list[Instance]:
        response = await self._get_authorized(url=f"{self._compute_host}/compute/v1/instances",
                                              params={"folderId": folder_id, "filter": "status='RUNNING'"})
        if response.status != 200:
            error = (await response.json())["message"]
            self._logger.error(f"Error getting vms from folder: {error}")
            return []
        res = await response.json()
        if res:
            vms = res["instances"]
            vms = [Instance().from_dict(item) for item in vms]
            return vms
        else:
            return []

    async def stop_vm(self, instance_id: str):
        response = await self._post_authorized(url=f"{self._compute_host}/compute/v1/instances/{instance_id}:stop",
                                               data={})
        if response.status != 200:
            error = (await response.json())["message"]
            self._logger.error(f"Error stopping vm {instance_id}: {error}")
        else:
            self._logger.info(f"Stopped vm {instance_id}")


async def auto_token_updater(api: YandexCloudAPI) -> None:
    while 1:
        await api.update_iam_token()

        await asyncio.sleep(60 * 60)


async def stop_expired_vms(api: YandexCloudAPI, interval: int):
    while 1:
        cloud_list = await api.get_cloud_list()
        for cloud in cloud_list:
            folders = await api.get_folders_in_cloud(cloud.id)
            for folder in folders:
                vms = await api.get_vms_in_folder(folder.id)
                today = datetime.now()
                for vm in vms:
                    if "expired_date" in vm.labels:
                        exp_date = datetime.strptime(vm.labels["expired_date"], "%d.%m.%Y")
                        if today > exp_date:
                            await api.stop_vm(instance_id=vm.id)
        await asyncio.sleep(interval)


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)

    api = YandexCloudAPI(os.getenv("YANDEX_OAUTH_TOKEN"))
    monitoring_interval = int(os.getenv("MONITORING_INTERVAL"))

    tasks = [
        auto_token_updater(api),
        stop_expired_vms(api, monitoring_interval)
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
