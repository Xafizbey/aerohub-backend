"""Language detection and field localisation helpers."""
from typing import Any, Literal

Lang = Literal["en", "ru", "kk", "ky"]
SUPPORTED: tuple[str, ...] = ("en", "ru", "kk", "ky")

# Fallback chain: if the requested lang has no translation, try these in order
_FALLBACK: dict[str, list[str]] = {
    "ky": ["kk", "ru", "en"],
    "kk": ["ru", "en"],
    "ru": ["en"],
    "en": [],
}


def resolve_lang(raw: str | None) -> Lang:
    """Normalise and validate a language code, default → 'en'."""
    if raw and raw.lower()[:2] in SUPPORTED:
        return raw.lower()[:2]  # type: ignore[return-value]
    return "en"


def localize(obj: Any, field: str, lang: str) -> Any:
    """
    Return the best localised value for *field* on *obj*.

    For lang='en'  → obj.{field}
    For lang='ru'  → obj.title_ru  or  obj.{field}
    For lang='kk'  → obj.title_kk  or  obj.{field}
    For lang='ky'  → obj.title_ky  or  obj.title_kk  or  obj.{field}
    """
    if lang == "en":
        return getattr(obj, field, None)

    # Try exact match first
    value = getattr(obj, f"{field}_{lang}", None)
    if value:
        return value

    # Walk fallback chain
    for fallback_lang in _FALLBACK.get(lang, []):
        if fallback_lang == "en":
            return getattr(obj, field, None)
        value = getattr(obj, f"{field}_{fallback_lang}", None)
        if value:
            return value

    return getattr(obj, field, None)


def apply_lang_to_movie(movie: Any, lang: str) -> dict:
    """
    Build a dict from movie ORM obj, replacing title/description
    with the best match for *lang*. Safe to pass as response_model dict.
    """
    from app.schemas.movie import MovieOut
    data = MovieOut.model_validate(movie).model_dump()
    data["title"] = localize(movie, "title", lang) or movie.title
    data["description"] = localize(movie, "description", lang)
    return data


def apply_lang_to_movie_list(movie: Any, lang: str) -> dict:
    from app.schemas.movie import MovieListOut
    data = MovieListOut.model_validate(movie).model_dump()
    data["title"] = localize(movie, "title", lang) or movie.title
    return data


def apply_lang_to_music(music: Any, lang: str) -> dict:
    from app.schemas.music import MusicOut
    data = MusicOut.model_validate(music).model_dump()
    data["title"] = localize(music, "title", lang) or music.title
    data["genre"] = localize(music, "genre", lang)
    return data


def apply_lang_to_category(cat: Any, lang: str) -> dict:
    from app.schemas.movie import CategoryOut
    data = CategoryOut.model_validate(cat).model_dump()
    data["name"] = localize(cat, "name", lang) or cat.name
    data["description"] = localize(cat, "description", lang)
    return data
