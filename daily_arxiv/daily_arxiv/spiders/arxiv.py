import scrapy
import os
import re


class ArxivSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = categories.split(",")
        # 保存目标分类列表，用于后续验证
        self.target_categories = set(map(str.strip, categories))
        self.start_urls = [
            f"https://arxiv.org/list/{cat}/new" for cat in self.target_categories
        ]  # 起始URL（计算机科学领域的最新论文）

    name = "arxiv"  # 爬虫名称
    allowed_domains = ["arxiv.org"]  # 允许爬取的域名

    @staticmethod
    def _clean_text(value: str) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    def _extract_categories(self, paper_dd) -> list[str]:
        # 优先从 primary-subject 里拿，然后再从完整 subjects 文本里补充
        primary_subject_text = self._clean_text(
            "".join(paper_dd.css(".list-subjects .primary-subject::text").getall())
        )
        full_subject_text = self._clean_text(
            "".join(paper_dd.css(".list-subjects::text").getall())
        )
        merged_subject_text = " ".join(
            [x for x in [primary_subject_text, full_subject_text] if x]
        )
        categories_in_paper = re.findall(r"\(([^)]+)\)", merged_subject_text)
        cleaned = [c.strip() for c in categories_in_paper if c.strip()]
        # 保持顺序去重
        return list(dict.fromkeys(cleaned))

    def parse(self, response):
        # 提取每篇论文的信息
        anchors = []
        for li in response.css("div[id=dlpage] ul li"):
            href = li.css("a::attr(href)").get()
            if href and "item" in href:
                anchors.append(int(href.split("item")[-1]))

        # 遍历每篇论文的详细信息
        for paper in response.css("dl dt"):
            paper_anchor = paper.css("a[name^='item']::attr(name)").get()
            if not paper_anchor:
                continue
                
            paper_id = int(paper_anchor.split("item")[-1])
            if anchors and paper_id >= anchors[-1]:
                continue

            # 获取论文ID
            abstract_link = paper.css("a[title='Abstract']::attr(href)").get()
            if not abstract_link:
                continue
                
            arxiv_id = abstract_link.split("/")[-1]
            
            # 获取对应的论文描述部分 (dd元素)
            paper_dd = paper.xpath("following-sibling::dd[1]")
            if not paper_dd:
                continue

            categories = self._extract_categories(paper_dd)
            category_set = set(categories)

            # 标题、作者、摘要、评论直接从 list 页面提取，避免逐篇 API 请求导致慢速
            title_raw = "".join(paper_dd.css(".list-title::text").getall())
            title = self._clean_text(title_raw.replace("Title:", "", 1))
            authors = [
                self._clean_text(a)
                for a in paper_dd.css(".list-authors a::text").getall()
                if self._clean_text(a)
            ]
            summary = self._clean_text(" ".join(paper_dd.css("p.mathjax::text").getall()))
            comment_raw = "".join(paper_dd.css(".list-comments::text").getall())
            comment = self._clean_text(comment_raw.replace("Comments:", "", 1))
            comment = comment or None

            if not category_set or category_set.intersection(self.target_categories):
                yield {
                    "id": arxiv_id,
                    "pdf": f"https://arxiv.org/pdf/{arxiv_id}",
                    "abs": f"https://arxiv.org/abs/{arxiv_id}",
                    "authors": authors,
                    "title": title,
                    "categories": categories,
                    "comment": comment,
                    "summary": summary,
                }
                self.logger.debug(
                    f"Found paper {arxiv_id} with categories {category_set if category_set else set()}"
                )
            else:
                self.logger.debug(
                    f"Skipped paper {arxiv_id} with categories {category_set} (not in target {self.target_categories})"
                )
