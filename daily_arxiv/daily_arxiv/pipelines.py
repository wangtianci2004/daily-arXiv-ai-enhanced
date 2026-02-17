# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import arxiv
import os


class DailyArxivPipeline:
    def __init__(self):
        self.page_size = 100
        # 默认关闭逐篇 API 补查，避免每篇 3s 节流导致总耗时过长
        # 如需补查缺失字段，可设置 ARXIV_METADATA_FALLBACK=true
        self.enable_fallback = (
            os.environ.get("ARXIV_METADATA_FALLBACK", "false").strip().lower()
            in {"1", "true", "yes", "on"}
        )
        delay_seconds = float(
            os.environ.get("ARXIV_API_DELAY_SECONDS", "3.0").strip() or "3.0"
        )
        # 仅在 fallback 开启时才初始化 API client
        self.client = (
            arxiv.Client(page_size=self.page_size, delay_seconds=max(0.0, delay_seconds))
            if self.enable_fallback
            else None
        )

    @staticmethod
    def _is_missing(item: dict, key: str) -> bool:
        value = item.get(key)
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ""
        if isinstance(value, list):
            return len(value) == 0
        return False

    def process_item(self, item: dict, spider):
        arxiv_id = item["id"]
        item.setdefault("pdf", f"https://arxiv.org/pdf/{arxiv_id}")
        item.setdefault("abs", f"https://arxiv.org/abs/{arxiv_id}")

        # Spider 已提取关键字段，默认直接返回（大幅提速）
        required_keys = ["authors", "title", "categories", "summary"]
        has_missing = any(self._is_missing(item, key) for key in required_keys)
        if (not has_missing) or (not self.enable_fallback):
            return item

        # 仅缺失字段时才回退到 API 补查
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(self.client.results(search))
        item["authors"] = item.get("authors") or [a.name for a in paper.authors]
        item["title"] = item.get("title") or paper.title
        item["categories"] = item.get("categories") or paper.categories
        item["comment"] = item.get("comment") or paper.comment
        item["summary"] = item.get("summary") or paper.summary
        return item
