import requests
import json
import re
import asyncio
import aiohttp
from .config import conf


API_URL = "http://127.0.0.1:6806/api/"
HEADERS = {"Content-Type": "application/json"}
TOKEN = conf["siyuan_token"]


async def post(url: str, **params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=params, headers=HEADERS) as resp:
            return await resp.json()


class ApiException(Exception):
    pass


class AuthCodeIncorrectException(Exception):
    pass


def parse_ial(text: str):
    ret = {}
    subs = re.finditer(r" (.+?)=\"(.+?)\"", text, flags=re.DOTALL)
    for sub in subs:
        ret[sub.group(1)] = sub.group(2)
    return ret


class Block:
    def __init__(self,
                 alias, box, content,
                 created, hash, ial, id, length,
                 markdown: str, memo, name,
                 next_id, parent_id, path,
                 previous_id, root_id, sort):
        self.alias = alias
        self.box = box
        self.content = content
        self.created = created
        self.hash = hash
        self.ial = ial
        self.id = id
        self.length = length
        self.markdown = markdown
        self.memo = memo
        self.name = name
        self.next_id = next_id
        self.parent_id = parent_id
        self.path = path
        self.previous_id = previous_id
        self.root_id = root_id
        self.sort = sort
        self.properties = parse_ial(self.ial)

    def __init__(self, dict):
        for x in dict:
            setattr(self, x, dict[x])
        self.properties = parse_ial(self.ial)


"""
BlockPool = {}
def get_block(dict) -> Block:
    ret = BlockPool.get(dict["id"])
    if ret is None:
        ret = Block(dict)
        BlockPool[dict["id"]] = ret
    return ret
"""


async def query_sql(SQL: str):
    result = await post(API_URL + "query/sql", stmt=SQL)
    if result["code"] == 0:
        return result["data"]
    raise ApiException(result)


class NullBlockException(Exception):
    pass


async def find_by_id(id: str) -> Block:
    res = await query_sql(r"SELECT * FROM blocks WHERE id='{}'".format(id))
    if len(res) <= 0:
        raise NullBlockException(id)
    return Block(res[0])


async def get_col_by_id(id: str, attr_name: str):
    # print("get_col_by_id", id, attr_name)
    res = await query_sql(
        r"SELECT {} FROM blocks WHERE id='{}'".format(attr_name, id))
    if len(res) <= 0:
        raise NullBlockException(id)
    return res[0][attr_name]


async def get_ial_by_id(id: str) -> str:
    return (await get_col_by_id(id, "ial")).replace("_esc_newline_", "\n")


class PropertyNotFoundException(Exception):
    pass


async def get_property_by_id(id: str, property_name: str):
    ial = await get_ial_by_id(id)
    match = re.search(r" {}=\"(.+?)\"".format(property_name),
                      ial, flags=re.DOTALL)
    if match is None:
        raise PropertyNotFoundException(id, property_name)
    res = match.group(1)
    return res


async def do_property_exist_by_id(id: str, property_name: str):
    # print(id)
    ial = await get_ial_by_id(id)
    return property_name in ial


async def get_sons_by_id(id: str):
    return await query_sql(r"SELECT id FROM blocks WHERE parent_id='{}'".format(id))


async def get_parent_by_id(id: str):
    # print("get parent by id: {} parent: {}".format(
    # id, get_col_by_id(id, "parent_id")))
    return await get_col_by_id(id, "parent_id")


async def set_attribute(id: str, attr: str, val: str):
    return await post(API_URL + "attr/setBlockAttrs", id=id, attrs={attr: val})


async def set_attributes(id: str, attrs):
    return await post(API_URL + "attr/setBlockAttrs", id=id, attrs=attrs)


async def export_md_content(id: str) -> str:
    result = await post(API_URL + "export/exportMdContent", id=id)
    if result["code"] == 0:
        return result["data"]["content"]
