import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import argparse
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Chrome Bookmarks")


def find_chrome_bookmarks():
    """查找Chrome书签文件路径"""
    home = Path.home()

    # 根据不同系统查找路径
    if os.name == "nt":  # Windows
        paths = [home / "AppData/Local/Google/Chrome/User Data/Default/Bookmarks"]
    elif os.name == "posix":  # macOS/Linux
        if os.uname().sysname == "Darwin":  # macOS
            paths = [
                home / "Library/Application Support/Google/Chrome/Default/Bookmarks"
            ]
        else:  # Linux
            paths = [home / ".config/google-chrome/Default/Bookmarks"]

    # 检查路径是否存在
    for path in paths:
        if path.exists():
            return path
    return None


def extract_bookmarks(node, folder=""):
    """递归提取书签"""
    bookmarks = []

    if "children" in node:
        for child in node["children"]:
            if child.get("type") == "url":
                bookmarks.append(
                    {
                        "title": child.get("name", ""),
                        "url": child.get("url", ""),
                        "folder": folder,
                    }
                )
            elif child.get("type") == "folder":
                folder_name = child.get("name", "")
                new_folder = f"{folder}/{folder_name}" if folder else folder_name
                bookmarks.extend(extract_bookmarks(child, new_folder))

    return bookmarks


@mcp.tool()
def get_bookmarks(limit: int = 20) -> list:
    """获取Chrome书签列表

    Args:
        limit: 返回的最大数量，默认20
    """
    bookmarks_path = find_chrome_bookmarks()

    if not bookmarks_path:
        return ["未找到Chrome书签文件"]

    try:
        with open(bookmarks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_bookmarks = []
        roots = data.get("roots", {})

        for root_key in ["bookmark_bar", "other", "synced"]:
            if root_key in roots:
                all_bookmarks.extend(extract_bookmarks(roots[root_key]))

        # 格式化输出
        result = []
        for i, bm in enumerate(all_bookmarks[:limit]):
            folder_info = f" ({bm['folder']})" if bm["folder"] else ""
            result.append(f"{i + 1}. {bm['title']}{folder_info}\n   {bm['url']}")

        if not result:
            return ["未找到书签"]

        return result

    except Exception as e:
        return [f"读取书签失败: {str(e)}"]


@mcp.tool()
def search_bookmarks(query: str, limit: int = 10) -> list:
    """搜索Chrome书签

    Args:
        query: 搜索关键词
        limit: 返回的最大数量，默认10
    """
    bookmarks_path = find_chrome_bookmarks()

    if not bookmarks_path:
        return ["未找到Chrome书签文件"]

    try:
        with open(bookmarks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        roots = data.get("roots", {})
        all_bookmarks = []
        for root_key in ["bookmark_bar", "other", "synced"]:
            if root_key in roots:
                all_bookmarks.extend(extract_bookmarks(roots[root_key]))

        # 搜索逻辑
        query_lower = query.lower()
        results = []

        for bm in all_bookmarks:
            if (
                query_lower in bm["title"].lower()
                or query_lower in bm["url"].lower()
                or query_lower in bm["folder"].lower()
            ):

                folder_info = f" ({bm['folder']})" if bm["folder"] else ""
                results.append(f"- {bm['title']}{folder_info}\n  {bm['url']}")

                if len(results) >= limit:
                    break

        if not results:
            return [f"未找到包含 '{query}' 的书签"]

        return results

    except Exception as e:
        return [f"搜索书签失败: {str(e)}"]


@mcp.resource("chrome://bookmarks")
def get_bookmarks_resource() -> str:
    """获取书签数据资源"""
    bookmarks_path = find_chrome_bookmarks()

    if not bookmarks_path:
        return json.dumps({"error": "Bookmarks file not found"}, ensure_ascii=False)

    try:
        with open(bookmarks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 只返回基本信息
        bookmarks = extract_bookmarks(data.get("roots", {}))
        return json.dumps(bookmarks[:50], ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chrome bookmarks MCP helper")
    parser.add_argument(
        "--list", action="store_true", help="Print bookmarks to stdout and exit"
    )
    parser.add_argument(
        "--search",
        "-q",
        type=str,
        help="Search bookmarks instead of starting the MCP server",
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Maximum number of bookmarks to print"
    )
    parser.add_argument(
        "--serve", action="store_true", help="Force starting the MCP server on stdio"
    )
    args = parser.parse_args()

    # CLI mode if user explicitly asks to list or search.
    if args.list or args.search:
        lines = (
            search_bookmarks(args.search, args.limit)
            if args.search
            else get_bookmarks(args.limit)
        )
        for line in lines:
            print(line)
    else:
        if not args.serve:
            print(
                "Starting MCP server on stdio. Use --list or --search for CLI output."
            )
        mcp.run(transport="stdio")
