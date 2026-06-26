def normalize_taxa_func_display_item(item) -> str:
    if isinstance(item, tuple) and len(item) == 2:
        return f"{item[0]} <{item[1]}>"
    return str(item)


def parse_taxa_func_display_item(item) -> tuple[str, str] | None:
    item = normalize_taxa_func_display_item(item)
    if " <" not in item or not item.endswith(">"):
        return None
    taxa, func_part = item.rsplit(" <", 1)
    return taxa, func_part[:-1]


def taxa_func_display_item_has_link(item, taxa_func_index, taxa_func_linked_dict=None) -> bool:
    parsed = parse_taxa_func_display_item(item)
    if parsed is None:
        return False
    taxa, func = parsed
    if taxa_func_linked_dict is None:
        return (taxa, func) in taxa_func_index
    return any(linked_func == func for linked_func, _peptide_num in taxa_func_linked_dict.get(taxa, []))


def filter_linked_tfnet_items(
    items,
    df_type: str,
    taxa_func_linked_dict,
    func_taxa_linked_dict,
    taxa_func_index=None,
) -> tuple[list, list]:
    df_type = df_type.lower()

    if df_type == "taxa":
        removed = [item for item in items if item not in taxa_func_linked_dict]
        kept = [item for item in items if item in taxa_func_linked_dict]
        return kept, removed

    if df_type == "functions":
        removed = [item for item in items if item not in func_taxa_linked_dict]
        kept = [item for item in items if item in func_taxa_linked_dict]
        return kept, removed

    if df_type == "taxa-functions":
        kept = [
            normalize_taxa_func_display_item(item)
            for item in items
            if taxa_func_display_item_has_link(item, taxa_func_index, taxa_func_linked_dict)
        ]
        removed = [
            normalize_taxa_func_display_item(item)
            for item in items
            if not taxa_func_display_item_has_link(item, taxa_func_index, taxa_func_linked_dict)
        ]
        return kept, removed

    raise ValueError(f"type should be taxa, functions or taxa-functions! but got: {df_type}")


def format_linked_taxa_func_index_preview(
    taxa_func_index,
    linked_filter,
    limit: int,
) -> tuple[list[str], int]:
    total = len(taxa_func_index)
    preview: list[str] = []
    chunk_size = max(limit, 1000)

    for start in range(0, total, chunk_size):
        if len(preview) >= limit:
            break
        chunk = taxa_func_index[start:start + chunk_size]
        chunk_items = [f"{taxa} <{func}>" for taxa, func in chunk]
        linked_chunk_items = linked_filter(chunk_items)
        for item in linked_chunk_items:
            preview.append(item)
            if len(preview) >= limit:
                break
    return preview, total
