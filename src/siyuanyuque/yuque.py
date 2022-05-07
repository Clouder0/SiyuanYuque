"""Basic Yuque API wrapper. The existing libraries are not satisfying."""
import aiohttp


class Yuque:
    """Yuque API Instance."""

    def __init__(self, token: str, base_url: str = "https://www.yuque.com/api/v2"):
        self.session = aiohttp.ClientSession(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "siyuanyuque",
                "X-Auth-Token": token,
            },
        )

    async def create_doc(
        self,
        namespace: str,
        title: str,
        slug: str,
        body: str,
    ) -> str:
        """Create a Yuque Doc and return its id.

        Args:
            namespace (str): which repo to create the doc in, format `{username}/{reponame}`
            title (str): doc title
            slug (str): doc slug, in the url
            body (str): doc body

        Returns:
            str: Yuque Doc id.
        """
        async with self.session.post(
            f"/repos/{namespace}/docs",
            data={"title": title, "slug": slug, "body": body, "format": "markdown"},
        ) as res:
            if not res.ok:
                raise Exception()
            return res.json()["data"]["id"]

    async def update_doc(
        self, namespace: str, id: str, title: str, slug: str, body: str
    ) -> None:
        async with self.session.put(
            f"repos/{namespace}/docs/{id}",
            data={"title": title, "slug": slug, "body": body, "_force_asl": 1},
        ) as res:
            if not res.ok:
                raise Exception()
