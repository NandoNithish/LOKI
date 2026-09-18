from core.retrieval.search import SearchResult, StorySearch

_story_search = StorySearch()


def add_story_document(
    source_id: str,
    text: str,
    metadata: dict | None = None,
) -> None:
    _story_search.add_document(
        source_id,
        text,
        metadata,
    )


def search_story(
    query: str,
    limit: int = 5,
) -> list[SearchResult]:
    return _story_search.search(query, limit)