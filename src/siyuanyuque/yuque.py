"""Basic Yuque API wrapper. The existing libraries are not satisfying."""
from __future__ import annotations

import httpx


class Yuque:
    """Yuque API Instance."""

    def __init__(self, token: str, base_url: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "api",
                "X-Auth-Token": token,
            },
        )

    def close(self) -> None:
        self.client.close()

    def create_doc(
        self,
        workspace: str,
        title: str,
        slug: str,
        body: str,
    ) -> str:
        """Create a Yuque Doc and return its id.

        Args:
            workspace (str): which repo to create the doc in, format `{username}/{reponame}`
            title (str): doc title
            slug (str): doc slug, in the url
            body (str): doc body

        Returns:
            str: Yuque Doc id.
        """
        res = self.client.post(
            f"/repos/{workspace}/docs",
            json={"title": title, "slug": slug, "body": body, "format": "markdown"},
        )
        return res.json()["data"]["id"]

    def update_doc(
        self, workspace: str, id: str, title: str, slug: str, body: str
    ) -> None:
        ret = self.client.put(
            f"/repos/{workspace}/docs/{id}",
            json={"title": title, "slug": slug, "body": body, "_force_asl": 1},
        )
        if ret.status_code != 200:
            raise Exception(ret)
