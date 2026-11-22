# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as kenpo


def test_article_count_and_numbering():
    assert len(kenpo.ARTICLES) == 103
    assert [a["n"] for a in kenpo.ARTICLES] == list(range(1, 104))
    assert all(a["paras"] and all(p.strip() for p in a["paras"]) for a in kenpo.ARTICLES)


def test_chapters_cover_all():
    assert set(kenpo.CHAPTERS) == set(range(1, 12))
    assert {a["chapter"] for a in kenpo.ARTICLES} == set(range(1, 12))
    assert kenpo.BY_NUMBER[9]["chapter"] == 2
    assert kenpo.BY_NUMBER[103]["chapter"] == 11


def test_famous_articles_text():
    assert "戦力は、これを保持しない" in "".join(kenpo.BY_NUMBER[9]["paras"])
    assert "健康で文化的な最低限度の生活" in "".join(kenpo.BY_NUMBER[25]["paras"])
    assert "国権の最高機関" in "".join(kenpo.BY_NUMBER[41]["paras"])
    assert len(kenpo.PREAMBLE) == 4


def test_kanji_number():
    assert kenpo.kanji_number(1) == "一"
    assert kenpo.kanji_number(9) == "九"
    assert kenpo.kanji_number(10) == "十"
    assert kenpo.kanji_number(25) == "二十五"
    assert kenpo.kanji_number(99) == "九十九"
    assert kenpo.kanji_number(100) == "百"
    assert kenpo.kanji_number(103) == "百三"
    assert kenpo.article_label(9) == "第九条"


def test_quote_text_format():
    q = kenpo.quote_text(kenpo.BY_NUMBER[9])
    assert q.startswith("日本国憲法 第九条")
    assert "出典：e-Gov法令検索" in q


def test_pages():
    c = kenpo.app.test_client()
    assert c.get("/healthz").get_json() == {"status": "ok"}
    assert c.get("/").status_code == 200
    assert c.get("/article/9").status_code == 200
    assert c.get("/article/999").status_code == 302
    assert "前文" in c.get("/preamble").get_data(as_text=True)
    assert "第百三条" in c.get("/all").get_data(as_text=True)


def test_search_and_api():
    c = kenpo.app.test_client()
    body = c.get("/search", query_string={"q": "戦争"}).get_data(as_text=True)
    assert "第九条" in body
    data = c.get("/api/article/25").get_json()
    assert data["article"] == 25 and "最低限度" in data["quote"]
    assert c.get("/api/article/999").status_code == 404
    rnd = c.get("/api/random").get_json()
    assert 1 <= rnd["article"] <= 103


def test_script_not_escaped():
    # 引用コピーJSがHTMLエスケープされず、そのまま実行可能な形で配信されること
    c = kenpo.app.test_client()
    body = c.get("/").get_data(as_text=True)
    assert "execCommand('copy')" in body
    assert "&#39;" not in body.split("<script>")[1].split("</script>")[0]
