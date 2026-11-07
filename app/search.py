"""Site search over the published guide pages (decision 045).

Two phases, the same shape RAG will use later:
- Indexing (once, at startup): every guide page is split into chunks, one per h2 section, and
  each chunk is stored in an in-memory SQLite FTS5 table with its link and the page's official
  sources. Content edits reach search after a restart (every deploy restarts the server).
- Searching (each request): the question is cleaned the same way as the chunks, FTS5 finds the
  chunks that contain its words, and bm25 ranks them (rare words and short sections count more).
"""

import html
import re
import sqlite3
import threading
from pathlib import Path

from app.content import list_slugs, load_page
from app.i18n import is_english, tf, tr
from app.universities import UNIVERSITIES_AR, count_ar, normalize

ENGLISH_STOPWORDS = {"a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it", "my", "of", "on", "or",
                     "the", "to", "what", "when", "where", "which", "who", "why", "with"}

# Arabic writes "the" and some small words joined to the next word: «المنحة» = «ال» + «منحة».
# Dropping them on both sides lets «منحة» find «المنحة» and «والمنحة». Words of 3 letters or
# fewer are kept whole so short words aren't cut to nothing.
ARABIC_PREFIXES = ("وال", "بال", "فال", "كال", "لل", "ال")

# Test and platform names written in Arabic letters or in English (decision 061): both spellings are
# stored and searched as the English name, so «دولينجو» finds «Duolingo» and the other way round.
# Keys are in search_form's own spelling (normalize: آ → ا, lower case; then the «ال» prefix dropped).
SYNONYMS = {
    "دولينجو": "duolingo", "دوولينجو": "duolingo", "دولنجو": "duolingo", "دولينقو": "duolingo",
    "ايلتس": "ielts", "ايلس": "ielts",
    "توفل": "toefl", "تويفل": "toefl",
    "سات": "sat",
    "يوكاس": "ucas",
}

# Words a question is built from that say nothing about its subject (هل، ما، متى، كيف…), dropped by retrieve().
# Students type dialect, so its fillers are in the list too; they are input words, never shown on a page, so the
# list lives in its own file (app/question_words.txt) beside the formal-Arabic test's scope (tests/test_content.py).
QUESTION_STOPWORDS = {w for line in (Path(__file__).parent / "question_words.txt").read_text(encoding="utf-8").splitlines()
                      if not line.startswith("#") for w in line.split()}

H2 = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
TAG = re.compile(r"<[^>]+>")
MAX_RESULTS = 10
SNIPPET_CHARS = 180


def strip_prefix(word):
    for prefix in ARABIC_PREFIXES:
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            return word[len(prefix):]
    return word


def search_form(text):
    """The form both chunks and questions are stored and searched in."""
    words = (strip_prefix(w) for w in normalize(text).split())
    return " ".join(SYNONYMS.get(w, w) for w in words)


def plain(fragment):
    """HTML → plain text: tags removed, entities decoded, spaces collapsed (none inside brackets
    or before punctuation, where a removed link tag would leave one)."""
    text = re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", fragment)))
    text = re.sub(r"([(«])\s+", r"\1", text)
    return re.sub(r"\s+([)».,،؛:؟!])", r"\1", text).strip()


def chunks_of(page, url):
    """One chunk for the text before the first h2 (with the page description), one per h2 section."""
    parts = H2.split(page["html"])  # [intro, id1, heading1, body1, id2, heading2, body2, ...]
    intro = " ".join(filter(None, [page.get("description"), plain(parts[0])]))
    chunks = [{"heading": None, "url": url, "text": intro}] if intro else []
    for i in range(1, len(parts), 3):
        chunks.append({"heading": plain(parts[i + 1]), "url": f"{url}#{parts[i]}", "text": plain(parts[i + 2])})
    return chunks


class SiteSearch:
    def __init__(self, program_slugs, paths_by_id, test_needs, explorer=None):
        # check_same_thread=False: FastAPI answers requests on several threads. The lock makes
        # them take turns on this one connection; each search takes well under a millisecond.
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.lock = threading.Lock()
        self.db.execute("CREATE VIRTUAL TABLE chunks USING fts5(title, heading, body, n UNINDEXED)")
        self.chunks = []

        # 1. Guide pages (content/), one chunk per section.
        pages = ([("grades", s) for s in list_slugs("grades")]
                 + [("programs", s) for s in program_slugs]
                 + [("resources", s) for s in list_slugs("resources")])
        for section, slug in pages:
            page = load_page(section, slug)
            # Only what the site publishes with official sources is searchable (CLAUDE.md, decision 028).
            if not page or page.get("status") != "sourced" or not page.get("sources"):
                continue
            for chunk in chunks_of(page, f"/{section}/{slug}"):
                self.add(page["title"], chunk["heading"], chunk["url"], chunk["text"], page["sources"])

        # 2. Program facts (data/paths.json): only the ones the program page shows, linked to the fact itself.
        for slug in program_slugs:
            program = paths_by_id[slug]
            labelled = [(None, f) for f in program.get("facts") or []]
            labelled += [(t["name_ar"], f) for t in program["tracks"] for f in t.get("facts") or []]
            for label, f in labelled:
                if f["status"] in ("sourced", "conflict") and f.get("sources"):
                    text = " ".join(filter(None, [tr(f["text_ar"]), tr(f.get("note_ar"))]))
                    self.add(tr(program["name_ar"]), tr(label), f"/programs/{slug}#fact-{f['id']}", text, f["sources"])

        # 3. «الاختبارات: من يطلب ماذا؟» (data/test_needs.json), shown on the ثاني ثانوي page.
        for row in test_needs["rows"]:
            if row.get("need_ar") and row.get("source", {}).get("url", "").startswith("http"):
                self.add(tr("الاختبارات: من يطلب ماذا؟"), tr(row["who_ar"]), "/grades/grade-11#tests-title",
                         tr(row["need_ar"]), [row["source"]])

        # 4. Each English test across the researched universities (decision 061), computed from
        # data/university_details/, so «duolingo» also answers "which universities accept it?".
        if explorer is not None:
            for slug, test in (("duolingo", "duolingo"), ("ielts", "ielts"), ("toefl", "toefl_ibt")):
                page = load_page("resources", slug)
                summary = explorer.test_summary(test)
                if not page or page.get("status") != "sourced" or not summary["groups"]:
                    continue
                counts = tr("، ").join(f"{tr(g['title_ar'])}: {len(g['rows'])}" for g in summary["groups"])
                text = tf("{label} في {count} من قوائم الابتعاث جمعنا متطلباتها. {counts}. الحد الأدنى والدرجة الموصى بها لكل جامعة، من صفحتها الرسمية.",
                          label=summary["label"], count=count_ar(summary["researched"], UNIVERSITIES_AR), counts=counts)
                self.add(page["title"], tf("{label} في جامعات القوائم", label=summary["label"]), f"/resources/{slug}#universities",
                         text, page["sources"])

    def add(self, title, heading, url, text, sources):
        self.db.execute("INSERT INTO chunks VALUES (?, ?, ?, ?)",
                        (search_form(title), search_form(heading or ""), search_form(text), len(self.chunks)))
        sources = [{**s, "title": tr(s["title"])} for s in sources]
        self.chunks.append({"title": title, "heading": heading, "url": url, "text": text, "sources": sources})

    def search(self, q):
        """The best chunks for q, most relevant first (at most MAX_RESULTS)."""
        words = search_form(q[:200]).split()[:12]
        # English questions carry small words the guide's text may not hold next to the real ones.
        if is_english():
            words = [w for w in words if w not in ENGLISH_STOPWORDS] or words
        if not words:
            return []
        # Each word in quotes (so FTS5 never reads it as an operator), with * so «تقد» finds «تقديم».
        # All words must appear (FTS5's default AND). A match in a section's heading weighs most: a section
        # named after the question beats a short fact that only mentions its words.
        match = " ".join(f'"{w}"*' for w in words)
        with self.lock:
            rows = self.db.execute(
                "SELECT n FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks, 3.0, 6.0, 1.0) LIMIT ?",
                (match, MAX_RESULTS)).fetchall()
        return [self.result(self.chunks[n], words) for (n,) in rows]

    def retrieve(self, question, k=5):
        """The retrieval step for وضّاح (docs/specs/agent.md §4): a whole question, in فصحى or dialect, as typed.

        search() needs every word to match, which suits a few search words but finds nothing for «هل أستطيع التقديم
        على مسار الرواد وأنا في ثالث ثانوي؟». Here the question words and fillers are dropped, any remaining word may
        match, and bm25 ranks the chunks that share the most (and rarest) words first. Same chunks, same sources."""
        words = [w for w in search_form(question[:500]).split()
                 if w not in QUESTION_STOPWORDS and w not in ENGLISH_STOPWORDS and len(w) > 1][:16]
        if not words:
            return []
        match = " OR ".join(f'"{w}"*' for w in dict.fromkeys(words))
        with self.lock:
            rows = self.db.execute(
                "SELECT n FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks, 3.0, 6.0, 1.0) LIMIT ?",
                (match, k)).fetchall()
        return [self.result(self.chunks[n], words) for (n,) in rows]

    def result(self, chunk, words):
        return {"title": chunk["title"], "heading": chunk["heading"], "url": chunk["url"],
                "snippet": snippet(chunk["text"], words), "sources": chunk["sources"]}


def snippet(text, words):
    """About SNIPPET_CHARS of the original text, starting near the first matching word."""
    start = 0
    for i, word in enumerate(text.split(" ")):
        if any(search_form(word).startswith(w) for w in words):
            start = len(" ".join(text.split(" ")[:i]))
            break
    start = max(0, start - 40)
    if start:
        start = text.find(" ", start) + 1  # begin on a whole word
    piece = text[start:start + SNIPPET_CHARS]
    if start + SNIPPET_CHARS < len(text):
        piece = piece[:piece.rfind(" ")] + "…"
    return ("…" if start else "") + piece
