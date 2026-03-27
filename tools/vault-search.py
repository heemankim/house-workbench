#!/usr/bin/env python3
"""Obsidian Vault FTS5 Indexer & Search CLI

Indexes markdown files in Obsidian vault with FTS5 fulltext search.
Supports Korean tokenization (kiwipiepy) for better CJK search.

CLI:
    python3 vault-search.py index --vault /path/to/vault
    python3 vault-search.py search "query" --limit 10
    python3 vault-search.py status

Schema (v4): Indexed columns: path, title, tags, tldr, para_category
             Unindexed: content_hash, updated_at, *_raw (preserve original)
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

_kiwi = None


def _get_kiwi():
    global _kiwi
    if _kiwi is None:
        try:
            from kiwipiepy import Kiwi
            _kiwi = Kiwi()
        except ImportError:
            return None
    return _kiwi


def _has_kiwipiepy():
    try:
        import kiwipiepy
        return True
    except ImportError:
        return False


def _tokenize_only(text):
    """Tokenize text without including original (for search queries)."""
    if not text:
        return text
    kiwi = _get_kiwi()
    if kiwi is None:
        return text
    tokens = kiwi.tokenize(text)
    result = []
    buf = []
    for t in tokens:
        is_single_korean = len(t.form) == 1 and _KOREAN_RE.match(t.form)
        if is_single_korean:
            buf.append(t.form)
        else:
            if buf:
                result.append("".join(buf))
                buf = []
            result.append(t.form)
    if buf:
        result.append("".join(buf))
    return " ".join(result)


SCHEMA_VERSION = "4"
DB_NAME = "vault-index.db"


def get_db_path():
    return Path(__file__).parent / DB_NAME


def init_db(conn):
    conn.execute("DROP TABLE IF EXISTS vault_docs")
    conn.execute("""
        CREATE VIRTUAL TABLE vault_docs USING fts5(
            path,
            title,
            tags,
            tldr,
            para_category,
            content_hash UNINDEXED,
            updated_at UNINDEXED,
            tags_raw UNINDEXED,
            tldr_raw UNINDEXED,
            title_raw UNINDEXED
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS db_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.execute(
        "INSERT OR REPLACE INTO db_meta (key, value) VALUES ('schema_version', ?)",
        (SCHEMA_VERSION,),
    )
    conn.commit()


def ensure_db(conn):
    """Create tables if they don't exist, or rebuild if schema is outdated."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='vault_docs'"
    )
    if cur.fetchone() is None:
        init_db(conn)
        return

    # Check schema version — rebuild if outdated (e.g. v1 -> v2 for pre-tokenize)
    try:
        ver = conn.execute(
            "SELECT value FROM db_meta WHERE key = 'schema_version'"
        ).fetchone()
        if ver is None or ver[0] != SCHEMA_VERSION:
            init_db(conn)
    except sqlite3.OperationalError:
        init_db(conn)


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content. Returns dict or empty dict."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
            fm[key] = items
        else:
            fm[key] = val.strip("\"'")
    return fm


def extract_tldr(content):
    """Extract TL;DR section or first 3 lines as fallback summary."""
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, count=1, flags=re.DOTALL)
    # Remove the title heading
    body = re.sub(r"^#\s+.*\n*", "", body.strip())

    tldr_match = re.search(
        r"##\s+TL;DR\s*\n(.*?)(?=\n##\s|\Z)", body, re.DOTALL | re.IGNORECASE
    )
    if tldr_match:
        return tldr_match.group(1).strip()[:500]

    lines = [l.strip() for l in body.strip().split("\n") if l.strip()]
    return "\n".join(lines[:3])[:500]


def infer_para_category(rel_path):
    """Map file path to PARA category (Projects/Areas/Resources/Archives)."""
    parts = Path(rel_path).parts
    if not parts:
        return "Inbox"
    first = parts[0]
    mapping = {
        "0-Inbox": "Inbox",
        "1-Projects": "Projects",
        "2-Areas": "Areas",
        "3-Resources": "Resources",
        "4-Archives": "Archives",
    }
    return mapping.get(first, "Other")


def content_hash(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()


_KOREAN_RE = re.compile(r"[\uac00-\ud7a3]")


def pre_tokenize(text):
    """Tokenize text for FTS5 indexing. Uses kiwipiepy for Korean morpheme splitting if available."""
    if not text:
        return text
    kiwi = _get_kiwi()
    if kiwi is None:
        return text
    tokens = kiwi.tokenize(text)

    # Post-process: rejoin consecutive single-char Korean tokens
    result = []
    buf = []
    for t in tokens:
        is_single_korean = len(t.form) == 1 and _KOREAN_RE.match(t.form)
        if is_single_korean:
            buf.append(t.form)
        else:
            if buf:
                result.append("".join(buf))
                buf = []
            result.append(t.form)
    if buf:
        result.append("".join(buf))

    return " ".join(result)


def scan_vault(vault_path):
    """Yield (relative_path, content) for all .md files."""
    vault = Path(vault_path)
    for md_file in sorted(vault.rglob("*.md")):
        if any(p.startswith(".") for p in md_file.relative_to(vault).parts):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            rel = str(md_file.relative_to(vault))
            yield rel, content
        except (UnicodeDecodeError, PermissionError):
            continue


def index_vault(vault_path, db_path=None):
    """Build or update FTS5 index incrementally using content hashes."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    ensure_db(conn)

    # Load existing hashes
    existing = {}
    try:
        for row in conn.execute("SELECT path, content_hash FROM vault_docs"):
            existing[row[0]] = row[1]
    except sqlite3.OperationalError:
        init_db(conn)

    seen_paths = set()
    stats = {"added": 0, "updated": 0, "unchanged": 0, "deleted": 0, "total": 0}

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    for rel_path, content in scan_vault(vault_path):
        seen_paths.add(rel_path)
        h = content_hash(content)

        if rel_path in existing and existing[rel_path] == h:
            stats["unchanged"] += 1
            stats["total"] += 1
            continue

        fm = parse_frontmatter(content)
        title_raw = Path(rel_path).stem
        title = pre_tokenize(title_raw)
        tags_raw = ", ".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else fm.get("tags", "")
        tags = pre_tokenize(tags_raw)
        tldr_raw = extract_tldr(content)
        tldr = pre_tokenize(tldr_raw)
        category = infer_para_category(rel_path)

        if rel_path in existing:
            conn.execute("DELETE FROM vault_docs WHERE path = ?", (rel_path,))
            stats["updated"] += 1
        else:
            stats["added"] += 1

        conn.execute(
            "INSERT INTO vault_docs (path, title, tags, tldr, para_category, content_hash, updated_at, tags_raw, tldr_raw, title_raw) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rel_path, title, tags, tldr, category, h, now, tags_raw, tldr_raw, title_raw),
        )
        stats["total"] += 1

    # Remove deleted files
    for old_path in existing:
        if old_path not in seen_paths:
            conn.execute("DELETE FROM vault_docs WHERE path = ?", (old_path,))
            stats["deleted"] += 1

    conn.commit()
    conn.close()
    return stats


def search(query, limit=10, category=None, db_path=None, vault_path=None):
    """Search indexed vault documents. Auto-syncs index before searching."""
    if db_path is None:
        db_path = get_db_path()

    # Auto-sync: re-index before search if vault_path provided
    if vault_path and os.path.isdir(vault_path):
        index_vault(vault_path, db_path)

    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    tokenized_query = _tokenize_only(query)

    sql = (
        "SELECT path, title, tags, tldr, para_category, rank, tags_raw, tldr_raw, title_raw "
        "FROM vault_docs WHERE vault_docs MATCH ? "
    )
    params = [tokenized_query]

    if category:
        sql += "AND para_category = ? "
        params.append(category)

    sql += "ORDER BY rank LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return []

    results = []
    for row in rows:
        raw_tags = row["tags_raw"] or row["tags"]
        raw_tldr = row["tldr_raw"] or row["tldr"]
        results.append({
            "path": row["path"],
            "title": row["title_raw"] or row["title"],
            "tags": [t.strip() for t in raw_tags.split(",") if t.strip()],
            "tldr": raw_tldr,
            "category": row["para_category"],
            "rank": round(row["rank"], 4),
        })

    conn.close()
    return results


def status(db_path=None):
    """Return DB status info."""
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return {"exists": False}

    conn = sqlite3.connect(str(db_path))
    total = conn.execute("SELECT COUNT(*) FROM vault_docs").fetchone()[0]

    categories = {}
    for row in conn.execute(
        "SELECT para_category, COUNT(*) FROM vault_docs GROUP BY para_category"
    ):
        categories[row[0]] = row[1]

    meta = {}
    try:
        for row in conn.execute("SELECT key, value FROM db_meta"):
            meta[row[0]] = row[1]
    except sqlite3.OperationalError:
        pass

    size_bytes = db_path.stat().st_size
    conn.close()

    return {
        "exists": True,
        "total_docs": total,
        "categories": categories,
        "db_size_kb": round(size_bytes / 1024, 1),
        "schema_version": meta.get("schema_version", "unknown"),
        "korean_tokenizer": _has_kiwipiepy(),
    }


def main():
    parser = argparse.ArgumentParser(description="Obsidian Vault FTS5 Indexer & Search")
    sub = parser.add_subparsers(dest="command")

    idx = sub.add_parser("index", help="Index vault files")
    idx.add_argument("--vault", required=True, help="Path to Obsidian vault")

    srch = sub.add_parser("search", help="Search indexed documents")
    srch.add_argument("query", help="Search query")
    srch.add_argument("--vault", help="Vault path (auto-syncs index before search)")
    srch.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    srch.add_argument("--category", help="Filter by PARA category")

    sub.add_parser("status", help="Show index status")

    args = parser.parse_args()

    if args.command == "index":
        vault = os.path.expanduser(args.vault)
        if not os.path.isdir(vault):
            print(json.dumps({"error": f"Vault not found: {vault}"}))
            sys.exit(1)
        stats = index_vault(vault)
        print(json.dumps(stats, ensure_ascii=False))

    elif args.command == "search":
        vault = os.path.expanduser(args.vault) if args.vault else None
        results = search(args.query, limit=args.limit, category=args.category, vault_path=vault)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "status":
        info = status()
        print(json.dumps(info, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
