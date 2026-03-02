#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Any

import markdown
from jinja2 import Template

INPUT_CANDIDATES = (Path("Docs/MetaX_Cookbook.md"), Path("docs/MetaX_Cookbook.md"))
MARKDOWN_EXTENSIONS = ["tables", "toc", "fenced_code", "sane_lists"]

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #ffffff;
            --text: #0f172a;
            --muted-text: #64748b;
            --accent: #0969da;
            --accent-strong: #0550ae;
            --link: #0969da;
            --surface: #ffffff;
            --surface-soft: #f6f8fa;
            --nav-bg: #f6f8fa;
            --nav-text: #24292f;
            --nav-border: #d0d7de;
            --nav-soft: #f3f4f6;
            --nav-soft-strong: #eaeef2;
            --active-bg: #ddf4ff;
            --active-border: #0969da;
            --table-border: #d0d7de;
            --table-head-bg: #f6f8fa;
            --table-stripe-odd: #ffffff;
            --table-stripe-even: #f9fbff;
            --code-bg: rgba(175, 184, 193, 0.2);
            --nav-width: 310px;
            --radius: 8px;
            --shadow: 0 1px 2px rgba(31, 35, 40, 0.04);
        }

        body.dark-mode {
            --bg: #0f172a;
            --text: #e6edf3;
            --muted-text: #9da7b3;
            --accent: #58a6ff;
            --accent-strong: #79c0ff;
            --link: #58a6ff;
            --surface: #161b22;
            --surface-soft: #21262d;
            --nav-bg: #161b22;
            --nav-text: #c9d1d9;
            --nav-border: #30363d;
            --nav-soft: #21262d;
            --nav-soft-strong: #30363d;
            --active-bg: rgba(56, 139, 253, 0.2);
            --active-border: #58a6ff;
            --table-border: #30363d;
            --table-head-bg: #1f2733;
            --table-stripe-odd: #161b22;
            --table-stripe-even: #1b2230;
            --code-bg: rgba(110, 118, 129, 0.4);
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
        }

        * {
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            margin: 0;
            color: var(--text);
            background: var(--bg);
            font-family: "Noto Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
        }

        nav {
            width: var(--nav-width);
            padding: 20px 16px;
            background: var(--nav-bg);
            color: var(--nav-text);
            border-right: 1px solid var(--nav-border);
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            overflow-y: auto;
            box-shadow: none;
            z-index: 1000;
        }

        .nav-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 12px;
        }

        .nav-title {
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }

        nav h2 {
            margin: 0;
            color: var(--nav-text);
            letter-spacing: 0;
            font-size: 1.18rem;
            white-space: nowrap;
        }

        .theme-toggle {
            border: 1px solid var(--nav-border);
            background: var(--nav-soft);
            color: var(--nav-text);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .theme-toggle:hover {
            background: var(--nav-soft-strong);
        }

        .sidebar-toggle {
            border: 1px solid var(--nav-border);
            background: var(--nav-soft);
            color: var(--nav-text);
            border-radius: 8px;
            width: 30px;
            height: 30px;
            line-height: 1;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .sidebar-toggle:hover {
            background: var(--nav-soft-strong);
        }

        .toc-actions {
            display: flex;
            gap: 8px;
            margin: 0 0 10px;
        }

        .toc-actions button {
            border: 1px solid var(--nav-border);
            background: var(--nav-soft);
            color: var(--nav-text);
            border-radius: 8px;
            padding: 3px 10px;
            font-size: 0.78rem;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .toc-actions button:hover {
            background: var(--nav-soft-strong);
        }

        .toc-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .toc-node {
            margin: 2px 0;
        }

        .toc-row {
            display: flex;
            align-items: center;
            gap: 4px;
            padding-left: calc((var(--toc-level) - 1) * 12px);
        }

        .toc-children {
            list-style: none;
            margin: 0;
            padding: 0;
        }

        .toc-caret,
        .toc-spacer {
            width: 18px;
            min-width: 18px;
            height: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .toc-caret {
            border: none;
            background: transparent;
            color: var(--nav-text);
            border-radius: 6px;
            cursor: pointer;
            opacity: 0.9;
            transition: transform 0.2s ease, background-color 0.2s ease;
        }

        .toc-caret::before {
            content: "▾";
            font-size: 0.78rem;
        }

        .toc-caret:hover {
            background: var(--nav-soft);
            opacity: 1;
        }

        .toc-node.collapsed > .toc-row .toc-caret {
            transform: rotate(-90deg);
        }

        .toc-node.collapsed > .toc-children {
            display: none;
        }

        nav a {
            display: block;
            padding: 6px 10px;
            color: var(--nav-text);
            text-decoration: none;
            line-height: 1.2;
            border-radius: 8px;
            font-size: 0.92rem;
            transition: all 0.2s ease;
            opacity: 0.9;
        }

        nav a.level-1 {
            font-weight: 600;
            font-size: 1rem;
            margin-top: 8px;
        }

        nav a.active {
            background-color: var(--active-bg);
            color: var(--accent-strong);
            border-left: 4px solid var(--active-border);
            opacity: 1;
        }

        nav a:hover {
            background-color: var(--nav-soft-strong);
            color: var(--text);
            opacity: 1;
        }

        nav a:focus-visible,
        .theme-toggle:focus-visible,
        .sidebar-toggle:focus-visible,
        .toc-caret:focus-visible,
        .toc-actions button:focus-visible,
        #backToTop:focus-visible,
        .toc-toggle:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }

        main {
            margin-left: var(--nav-width);
            padding: 36px 42px;
            min-height: 100vh;
            --list-indent: 0px;
        }

        main > * {
            max-width: 1100px;
        }

        main ul,
        main ol {
            padding-left: 24px;
            --list-indent: calc(var(--list-indent) + 24px);
        }

        main li > figure.image-wrap,
        main li > .table-responsive {
            margin-left: calc(-1 * var(--list-indent));
            width: calc(100% + var(--list-indent));
        }

        h1, h2, h3, h4 {
            scroll-margin-top: 84px;
        }

        h1 {
            border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
            margin-top: 0;
            font-size: 1.85rem;
        }

        h2 {
            color: var(--accent);
        }

        h3 {
            color: var(--link);
        }

        p, li {
            color: var(--text);
        }

        a {
            color: var(--link);
        }

        table {
            width: 100%;
            margin-bottom: 1rem;
            color: var(--text);
            border-collapse: collapse;
            box-shadow: none;
            border-radius: var(--radius);
            background: var(--surface);
            overflow: hidden;
            font-size: 0.95rem;
        }

        table th,
        table td {
            padding: 0.75rem;
            vertical-align: top;
            border-top: 1px solid var(--table-border);
        }

        table thead th {
            background: var(--table-head-bg);
            font-weight: 600;
            border-top: none;
        }

        table tbody tr:nth-child(odd) {
            background: var(--table-stripe-odd);
        }

        table tbody tr:nth-child(even) {
            background: var(--table-stripe-even);
        }

        table tbody tr:hover {
            background: var(--active-bg);
        }

        .table-responsive {
            display: block;
            width: max-content;
            max-width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border-radius: var(--radius);
            margin: 14px auto;
            background: var(--surface);
        }

        .image-wrap {
            display: block;
            width: 100%;
            margin: 20px auto;
            text-align: center;
        }

        .image-wrap img.doc-image {
            max-width: min(100%, 900px);
            min-width: min(100%, 300px);
            height: auto;
            display: block;
            margin: 0 auto;
            border: 1px solid var(--table-border);
            box-shadow: none;
            border-radius: 8px;
            background: var(--surface);
        }

        .table-responsive > table {
            margin: 0 auto;
            width: auto !important;
            min-width: 100%;
        }

        pre,
        code {
            border-radius: 8px;
            font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace;
        }

        pre {
            background: var(--surface-soft);
            padding: 14px 16px;
            border: 1px solid var(--table-border);
            overflow-x: auto;
            line-height: 1.45;
            margin: 1rem 0;
        }

        code {
            background: var(--code-bg);
            padding: 0.1em 0.35em;
            font-size: 0.92em;
        }

        pre code {
            background: transparent;
            padding: 0;
            border-radius: 0;
            font-size: 0.9rem;
            color: inherit;
        }

        ul.media-list,
        ol.media-list {
            padding-left: 0;
            margin-left: 0;
        }

        li.media-item {
            list-style: none;
            margin: 0.4rem 0 0.9rem;
            padding-left: 0;
        }

        li.media-item::marker {
            content: "";
        }

        #backToTop {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: none;
            background-color: var(--accent-strong);
            color: #ffffff;
            border: 1px solid transparent;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            box-shadow: none;
            z-index: 1010;
        }

        #backToTop:hover {
            background-color: var(--accent);
        }

        .toc-toggle {
            display: none;
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 1200;
            border: 1px solid transparent;
            background: var(--accent-strong);
            color: #ffffff;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.92rem;
            box-shadow: none;
            cursor: pointer;
        }

        @media (min-width: 961px) {
            body.sidebar-collapsed nav {
                width: 86px;
                padding-left: 10px;
                padding-right: 10px;
            }

            body.sidebar-collapsed main {
                margin-left: 86px;
                padding-left: 24px;
                padding-right: 24px;
            }

            body.sidebar-collapsed .toc-actions,
            body.sidebar-collapsed .toc-list,
            body.sidebar-collapsed .theme-toggle,
            body.sidebar-collapsed .nav-title-text {
                display: none;
            }
        }

        @media (max-width: 960px) {
            nav {
                width: calc(100% - 24px);
                left: 12px;
                top: 58px;
                height: auto;
                max-height: 0;
                overflow: hidden;
                border-radius: 14px;
                border-right: none;
                padding-top: 0;
                padding-bottom: 0;
                transition: max-height 0.25s ease, padding 0.25s ease;
            }

            nav.open {
                max-height: 72vh;
                overflow-y: auto;
                padding-top: 16px;
                padding-bottom: 16px;
            }

            main {
                margin-left: 0;
                padding: 70px 16px 24px;
            }

            .toc-toggle {
                display: inline-flex;
                align-items: center;
            }
        }
    </style>
</head>
<body>

<button id="tocToggle" class="toc-toggle" type="button" aria-expanded="false" aria-controls="doc-nav">Contents</button>

{% macro render_node(node) -%}
<li class="toc-node level-{{ node.level }}" data-anchor="{{ node.anchor }}" data-has-children="{{ 'true' if node.children else 'false' }}">
    <div class="toc-row" style="--toc-level: {{ node.level }};">
        {% if node.children %}
        <button class="toc-caret" type="button" aria-label="Toggle {{ node.title }}" aria-expanded="true"></button>
        {% else %}
        <span class="toc-spacer" aria-hidden="true"></span>
        {% endif %}
        <a class="nav-link toc-link level-{{ node.level }}" href="#{{ node.anchor }}" id="nav-{{ node.anchor }}">{{ node.title }}</a>
    </div>
    {% if node.children %}
    <ul class="toc-children">
    {% for child in node.children %}
        {{ render_node(child) }}
    {% endfor %}
    </ul>
    {% endif %}
</li>
{%- endmacro %}

<nav id="doc-nav" aria-label="Table of contents">
    <div class="nav-header">
        <div class="nav-title">
            <h2 class="nav-title-text">{{ title }}</h2>
            <button id="sidebarToggle" class="sidebar-toggle" type="button" aria-label="Collapse sidebar">◀</button>
        </div>
        <button id="toggleTheme" class="theme-toggle" type="button" aria-label="Toggle color theme">Dark</button>
    </div>
    <div class="toc-actions">
        <button id="collapseAllToc" type="button">Collapse All</button>
        <button id="expandAllToc" type="button">Expand All</button>
    </div>
    <ul class="toc-list">
    {% for node in toc_tree %}
        {{ render_node(node) }}
    {% endfor %}
    </ul>
</nav>

<main id="doc-main">
    {{ content }}
</main>

<button id="backToTop" type="button" aria-label="Back to top">Top</button>

<script>
    const THEME_KEY = "metax-docs-theme";
    const TOC_COLLAPSE_KEY = "metax-docs-collapsed-anchors";
    const SIDEBAR_COLLAPSE_KEY = "metax-docs-sidebar-collapsed";
    const MOBILE_BREAKPOINT = 960;

    const body = document.body;
    const nav = document.getElementById("doc-nav");
    const tocToggle = document.getElementById("tocToggle");
    const themeToggle = document.getElementById("toggleTheme");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const collapseAllToc = document.getElementById("collapseAllToc");
    const expandAllToc = document.getElementById("expandAllToc");
    const backToTop = document.getElementById("backToTop");
    const navLinks = Array.from(document.querySelectorAll("nav a.nav-link"));
    const tocNodes = Array.from(document.querySelectorAll(".toc-node"));
    const tocCarets = Array.from(document.querySelectorAll(".toc-caret"));
    const sections = Array.from(document.querySelectorAll("main h1, main h2, main h3, main h4, main h5, main h6")).filter(function(node) {
        return Boolean(node.id);
    });

    function collapsibleNodes() {
        return tocNodes.filter(function(node) {
            return node.getAttribute("data-has-children") === "true";
        });
    }

    function nodeCaret(node) {
        return node.querySelector(".toc-row .toc-caret");
    }

    function setNodeCollapsed(node, collapsed) {
        node.classList.toggle("collapsed", collapsed);
        const caret = nodeCaret(node);
        if (caret) {
            caret.setAttribute("aria-expanded", String(!collapsed));
        }
    }

    function saveCollapsedTocState() {
        const collapsedAnchors = collapsibleNodes()
            .filter(function(node) {
                return node.classList.contains("collapsed");
            })
            .map(function(node) {
                return node.getAttribute("data-anchor");
            });
        localStorage.setItem(TOC_COLLAPSE_KEY, JSON.stringify(collapsedAnchors));
    }

    function loadCollapsedTocState() {
        let collapsed = [];
        try {
            collapsed = JSON.parse(localStorage.getItem(TOC_COLLAPSE_KEY) || "[]");
        } catch (error) {
            collapsed = [];
        }
        const collapsedSet = new Set(collapsed);
        collapsibleNodes().forEach(function(node) {
            const anchor = node.getAttribute("data-anchor");
            setNodeCollapsed(node, collapsedSet.has(anchor));
        });
    }

    function applyTheme(theme) {
        const dark = theme === "dark";
        body.classList.toggle("dark-mode", dark);
        themeToggle.textContent = dark ? "Light" : "Dark";
    }

    function updateActiveNavLink() {
        if (!sections.length) {
            return;
        }

        const threshold = 120;
        let currentId = sections[0].id;

        sections.forEach(function(section) {
            if (section.getBoundingClientRect().top <= threshold) {
                currentId = section.id;
            }
        });

        navLinks.forEach(function(link) {
            const isActive = link.getAttribute("href") === "#" + currentId;
            link.classList.toggle("active", isActive);
        });

        const activeLink = document.querySelector('nav a.nav-link[href="#' + currentId + '"]');
        if (activeLink) {
            let currentNode = activeLink.closest(".toc-node");
            while (currentNode) {
                setNodeCollapsed(currentNode, false);
                currentNode = currentNode.parentElement.closest(".toc-node");
            }
        }
    }

    function updateBackToTop() {
        backToTop.style.display = window.scrollY > 300 ? "block" : "none";
    }

    function closeMobileToc() {
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            nav.classList.remove("open");
            tocToggle.setAttribute("aria-expanded", "false");
        }
    }

    function normalizeMediaLists() {
        document.querySelectorAll("ul, ol").forEach(function(list) {
            const items = Array.from(list.children).filter(function(child) {
                return child.tagName === "LI";
            });
            if (!items.length) {
                return;
            }

            const mediaOnly = items.every(function(item) {
                return item.classList.contains("media-item");
            });

            if (mediaOnly) {
                list.classList.add("media-list");
            }
        });
    }

    function setSidebarCollapsed(collapsed) {
        body.classList.toggle("sidebar-collapsed", collapsed);
        sidebarToggle.textContent = collapsed ? "▶" : "◀";
        sidebarToggle.setAttribute("aria-label", collapsed ? "Expand sidebar" : "Collapse sidebar");
        localStorage.setItem(SIDEBAR_COLLAPSE_KEY, collapsed ? "1" : "0");
    }

    themeToggle.addEventListener("click", function() {
        const nextTheme = body.classList.contains("dark-mode") ? "light" : "dark";
        applyTheme(nextTheme);
        localStorage.setItem(THEME_KEY, nextTheme);
    });

    tocToggle.addEventListener("click", function() {
        const open = nav.classList.toggle("open");
        tocToggle.setAttribute("aria-expanded", String(open));
    });

    navLinks.forEach(function(link) {
        link.addEventListener("click", closeMobileToc);
    });

    tocCarets.forEach(function(caret) {
        caret.addEventListener("click", function(event) {
            const node = event.currentTarget.closest(".toc-node");
            const collapsed = node.classList.contains("collapsed");
            setNodeCollapsed(node, !collapsed);
            saveCollapsedTocState();
        });
    });

    collapseAllToc.addEventListener("click", function() {
        collapsibleNodes().forEach(function(node) {
            setNodeCollapsed(node, true);
        });
        saveCollapsedTocState();
    });

    expandAllToc.addEventListener("click", function() {
        collapsibleNodes().forEach(function(node) {
            setNodeCollapsed(node, false);
        });
        saveCollapsedTocState();
    });

    sidebarToggle.addEventListener("click", function() {
        const collapsed = !body.classList.contains("sidebar-collapsed");
        setSidebarCollapsed(collapsed);
    });

    backToTop.addEventListener("click", function() {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", function() {
        updateBackToTop();
        updateActiveNavLink();
    }, { passive: true });

    window.addEventListener("resize", function() {
        if (window.innerWidth > MOBILE_BREAKPOINT) {
            nav.classList.remove("open");
            tocToggle.setAttribute("aria-expanded", "false");
        }
    });

    document.addEventListener("DOMContentLoaded", function() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        applyTheme(savedTheme === "dark" ? "dark" : "light");
        normalizeMediaLists();
        loadCollapsedTocState();
        setSidebarCollapsed(localStorage.getItem(SIDEBAR_COLLAPSE_KEY) === "1");
        updateActiveNavLink();
        updateBackToTop();
    });
</script>

</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert cookbook markdown to a styled HTML page.")
    parser.add_argument("--input", type=Path, help="Path to markdown source file.")
    parser.add_argument("--output", type=Path, help="Path to generated HTML output file.")
    parser.add_argument("--title", default="MetaX", help="Document title shown in the page header.")
    return parser.parse_args()


def resolve_markdown_path(cli_input: Path | None) -> Path:
    if cli_input is not None:
        if not cli_input.exists():
            raise FileNotFoundError(f"Input markdown file not found: {cli_input}")
        return cli_input

    for path in INPUT_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError("Could not find cookbook markdown file in Docs/ or docs/.")


def strip_html(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def collect_toc_tree(toc_tokens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def walk(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tree: list[dict[str, Any]] = []
        for node in nodes:
            level = int(node.get("level", 1))
            title = strip_html(str(node.get("name", "")))
            anchor = str(node.get("id", "")).strip()
            if not anchor or not title:
                continue
            tree.append(
                {
                    "level": level,
                    "title": title,
                    "anchor": anchor,
                    "children": walk(node.get("children", [])),
                }
            )
        return tree

    return walk(toc_tokens)


def ensure_class(attrs: str, class_names: list[str]) -> str:
    attrs = attrs.strip()
    if not attrs:
        return f'class="{" ".join(class_names)}"'

    class_match = re.search(r'class\s*=\s*["\']([^"\']*)["\']', attrs)
    if class_match:
        existing = class_match.group(1).split()
        merged = " ".join(dict.fromkeys(existing + class_names))
        return re.sub(
            r'class\s*=\s*["\']([^"\']*)["\']',
            f'class="{merged}"',
            attrs,
            count=1,
        )

    return f'{attrs} class="{" ".join(class_names)}"'


def enhance_tables(html_content: str) -> str:
    def replace_table_open(match: re.Match[str]) -> str:
        attrs = ensure_class(match.group(1) or "", ["table", "table-striped", "table-bordered"])
        return f'<div class="table-responsive"><table {attrs}>'

    html_content = re.sub(r"<table(\s[^>]*)?>", replace_table_open, html_content)
    html_content = re.sub(r"</table>", r"</table></div>", html_content)
    return html_content


def enhance_images(html_content: str) -> str:
    pattern = re.compile(r"<img\b([^>]*?)\s*/?>")

    def replace_image(match: re.Match[str]) -> str:
        attrs = ensure_class(match.group(1) or "", ["doc-image"])
        return f'<figure class="image-wrap"><img {attrs}></figure>'

    return pattern.sub(replace_image, html_content)


def normalize_internal_links(html_content: str) -> str:
    return re.sub(
        r'href="##([^"]+)"',
        lambda m: f'href="#{re.sub(r"[^a-zA-Z0-9]+", "-", m.group(1).strip()).lower().strip("-")}"',
        html_content,
    )


def cleanup_block_wrappers(html_content: str) -> str:
    # Avoid invalid <p><figure></figure></p> markup that can break centering in browsers.
    html_content = re.sub(
        r"<p>\s*(<figure class=\"image-wrap\">.*?</figure>)\s*</p>",
        r"\1",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r"<p>\s*(<div class=\"table-responsive\">.*?</div>)\s*</p>",
        r"\1",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r"<li>\s*(<figure class=\"image-wrap\">.*?</figure>)\s*</li>",
        r'<li class="media-item">\1</li>',
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r"<li>\s*(<div class=\"table-responsive\">.*?</div>)\s*</li>",
        r'<li class="media-item">\1</li>',
        html_content,
        flags=re.DOTALL,
    )
    return html_content


def build_html(markdown_path: Path, output_path: Path, title: str) -> None:
    markdown_content = markdown_path.read_text(encoding="utf-8")
    markdown_content = markdown_content.replace("# Contents", "").replace("[TOC]", "")

    md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)
    html_content = md.convert(markdown_content)
    toc_tree = collect_toc_tree(getattr(md, "toc_tokens", []))

    html_content = enhance_tables(html_content)
    html_content = enhance_images(html_content)
    html_content = normalize_internal_links(html_content)
    html_content = cleanup_block_wrappers(html_content)

    template = Template(TEMPLATE)
    html_output = template.render(content=html_content, toc_tree=toc_tree, title=title)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_output, encoding="utf-8")


def main() -> None:
    args = parse_args()
    markdown_path = resolve_markdown_path(args.input)
    output_path = args.output or markdown_path.with_name("index.html")

    build_html(markdown_path, output_path, args.title)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
