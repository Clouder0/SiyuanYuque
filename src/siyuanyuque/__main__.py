from __future__ import annotations

import asyncio
import datetime
import re
import time

from siyuanhelper.api import Siyuan, SiyuanBlock
from siyuanyuque.config import settings
from siyuanyuque.yuque import Yuque


class Sync:
    def __init__(self) -> None:
        self.siyuan = Siyuan(token=settings["siyuan_token"])
        self.yuque = Yuque(settings["user_token"], settings["api_host"])
        self.handled: list[str] = []

    async def create_doc(self, block: SiyuanBlock, workspace: str, slug: str) -> None:
        await block.ensure()
        print(f"creating doc {block.content}")
        ret = self.yuque.create_doc(
            workspace,
            block.content,
            slug,
            await self.export_siyuan_content(block.id, workspace),
        )
        if int(ret) > 0:
            block.attrs.set("custom-yuque-id", ret)
            print("Added {block.content} successfully.")
        else:
            print("Create {block.content} failed.")

    async def update_doc(
        self, block: SiyuanBlock, id: str, workspace: str, slug: str
    ) -> None:
        await block.ensure()
        print(f"updating doc {block.content}")
        try:
            self.yuque.update_doc(
                workspace,
                id,
                block.content,
                slug,
                await self.export_siyuan_content(block, workspace),
            )
            print(f"Updated {block.content} successfully.")
        except Exception as e:
            print("Exception occured when updating doc.")
            print(e)
            await self.create_doc(block, workspace, slug)

    async def export_siyuan_content(self, block: SiyuanBlock, workspace: str) -> str:
        ret = await block.export()
        if "assets_replacement" in settings:
            ret = ret.replace("(assets/", f"({settings['assets_replacement']}/")
        ret = ret.replace("siyuan://blocks", f"https://www.yuque.com/{workspace}")
        matches = re.finditer(r"\$(.+?)\$", ret)
        for x in matches:
            ret = ret.replace(x.group(0), f"${x.group(1).strip()}$")
        return ret

    async def exit(self) -> None:
        await self.siyuan.close()
        self.yuque.close()

    async def execute(self) -> None:
        start_time = time.perf_counter()
        all_blocks = await self.siyuan.get_blocks_by_sql(
            cond="WHERE id IN ("
            "SELECT block_id FROM attributes AS a WHERE a.name ='custom-yuque' AND a.value = 'true'"
            f") AND type='d' AND updated>'{settings['last_sync_time']}'"
        )
        tasks = [asyncio.create_task(self.handle_block(x)) for x in all_blocks]
        custom_sync = settings["custom_sync"]
        for x in custom_sync:
            tasks.extend(await self.handle_custom_sync(x))
        await asyncio.gather(*tasks)
        settings["last_sync_time"] = datetime.datetime.now().strftime(r"%Y%m%d%H%M%S")
        end_time = time.perf_counter()
        print(f"Finished. Total time: {end_time - start_time}s.")

    async def handle_block(self, block: SiyuanBlock, workspace: str = "") -> None:
        if block.id in self.handled:
            return
        try:
            self.handled.append(block.id)
            attr_workspace = await block.attrs.get("custom-yuque-workspace")
            workspace = attr_workspace if attr_workspace != "" else workspace
            if workspace == "":
                raise Exception("No workspace Exception.", block)
            yuque_id = await block.attrs.get("custom-yuque-id")
            slug = await block.attrs.get("custom-yuque-slug")
            slug = block.id if slug == "" else slug
            if id == "":
                await self.create_doc(block, workspace, slug)
            else:
                await self.update_doc(block, yuque_id, workspace, slug)
        except Exception as e:
            print(f"Exception Occured when handling block {block.id}")
            print(e)

    async def handle_custom_sync(self, sync: dict) -> list:
        block_ids = await self.siyuan.sql_query(
            sync["sql"] + f" AND updated > '{settings['last_sync_time']}'"
        )
        ret = []
        for x in block_ids:
            ret.append(
                asyncio.create_task(
                    self.handle_block(
                        await self.siyuan.get_block_by_id(x["id"]),
                        workspace=sync["yuque-workspace"],
                    )
                )
            )
        return ret


async def async_main() -> None:
    sync = Sync()
    await sync.execute()
    await sync.exit()


def main() -> None:
    asyncio.run(async_main())
