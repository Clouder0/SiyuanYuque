import asyncio
import datetime
from . import siyuanHelper as siyuan
from yuque_py import Yuque
from .config import conf
from . import config
import time


yuque = Yuque(api_host=conf["api_host"], user_token=conf["user_token"])


async def handle_id(block):
    attrs = siyuan.parse_ial(block["ial"])
    if "custom-yuque-id" in attrs:
        ret = yuque.docs.update(attrs["custom-yuque-workspace"], attrs["custom-yuque-id"], {
            "title": block["content"],
            "slug": block["id"],
            "public": 1,
            "body": await siyuan.export_md_content(block["id"]),
            "_force_asl": 1
        })
    else:
        if "custom-yuque-workspace" not in attrs:
            raise Exception("Yuque workspace not set.")
        ret = yuque.docs.create(attrs["custom-yuque-workspace"], {
            "title": block["content"],
            "slug": block["id"],
            "public": 1,
            "body": await siyuan.export_md_content(block["id"])
        })
        if ret["data"]["id"] > 0:
            await siyuan.set_attribute(block["id"], "custom-yuque-id", str(ret["data"]["id"]))
            print("Added {} successfully.".format(block["content"]))


async def execute():
    start_time = time.perf_counter()
    all_blocks = await siyuan.query_sql("SELECT * FROM blocks WHERE id IN ( SELECT block_id FROM attributes AS a WHERE a.name ='custom-yuque' AND a.value = 'true') AND type='d' AND updated>'{}'".format(conf["last_sync_time"]))
    await asyncio.gather(*[handle_id(x) for x in all_blocks])
    conf["last_sync_time"] = datetime.datetime.now().strftime(r"%Y%m%d%H%M%S")
    config.write_conf()
    end_time = time.perf_counter()
    print("Finished. Total time: {}s.".format(end_time - start_time))


if __name__ == "__main__":
    asyncio.run(execute())
