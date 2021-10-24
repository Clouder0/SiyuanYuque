import asyncio
import datetime
from . import siyuanHelper as siyuan
from yuque_py import Yuque
from .config import conf
from . import config
import time


yuque = Yuque(api_host=conf["api_host"], user_token=conf["user_token"])
handled = []


async def create_doc(block, id="", workspace="", public=1, slug=""):
    if workspace == "":
        raise Exception("Yuque workspace not set.")
    print("creating doc {}.".format(block["content"]))
    ret = yuque.docs.create(workspace, {
        "title": block["content"],
        "slug": slug,
        "public": public,
        "body": await siyuan.export_md_content(block["id"])
    })
    if ret["data"]["id"] > 0:
        await siyuan.set_attribute(block["id"], "custom-yuque-id", str(ret["data"]["id"]))
        print("Added {} successfully.".format(block["content"]))


async def export_siyuan_content_by_id(id):
    ret = await siyuan.export_md_content(id)
    ret = ret.replace(
        r"(assets/", r"({}/".format(conf.get("assets_replacement", "assets")))
    return ret


async def update_doc(block, id="", workspace="", public=1, slug=""):
    print("updating doc {}".format(block["content"]))
    ret = yuque.docs.update(workspace, id, {
        "title": block["content"],
        "slug": slug,
        "public": public,
        "body": await export_siyuan_content_by_id(block["id"]),
        "_force_asl": 1
    })
    if ret["data"]["id"] > 0:
        print("Updated {} successfully.".format(block["content"]))
    else:
        create_doc(block, id, workspace, public, slug)


async def handle_block(block, id="", workspace="", public=1, slug=""):
    if block["id"] in handled:
        return
    handled.append(block["id"])
    attrs = siyuan.parse_ial(block["ial"])
    workspace = attrs.get("custom-yuque-workspace", workspace)
    id = attrs.get("custom-yuque-id", id)
    if slug == "":
        slug = attrs.get("custom-yuque-slug", block["id"])
    public = int(attrs.get("custom-yuque-public", public))
    if id == "":
        await create_doc(block, id, workspace, public, slug)
    else:
        await update_doc(block, id, workspace, public, slug)


async def handle_custom_sync(sync):
    blocks = await siyuan.query_sql(sync["sql"] + " AND updated > '{}'".format(conf["last_sync_time"]))
    await asyncio.gather(*[handle_block(x, workspace=sync["yuque-workspace"]) for x in blocks])


async def execute():
    start_time = time.perf_counter()
    all_blocks = await siyuan.query_sql("SELECT * FROM blocks WHERE id IN ( SELECT block_id FROM attributes AS a WHERE a.name ='custom-yuque' AND a.value = 'true') AND type='d' AND updated>'{}'".format(conf["last_sync_time"]))
    tasks = [asyncio.create_task(handle_block(x)) for x in all_blocks]
    if "custom_sync" in conf:
        for x in conf["custom_sync"]:
            tasks.append(asyncio.create_task(handle_custom_sync(x)))
    await asyncio.gather(*tasks)
    conf["last_sync_time"] = datetime.datetime.now().strftime(r"%Y%m%d%H%M%S")
    config.write_conf()
    end_time = time.perf_counter()
    print("Finished. Total time: {}s.".format(end_time - start_time))


if __name__ == "__main__":
    asyncio.run(execute())
