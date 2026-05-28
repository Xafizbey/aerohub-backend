from pydantic import BaseModel


class DestinationPhotoOut(BaseModel):
    id: int
    photo_path: str
    caption: str | None = None
    caption_ru: str | None = None
    caption_kk: str | None = None
    caption_ky: str | None = None
    display_order: int = 0

    model_config = {"from_attributes": True}


class DestinationListItem(BaseModel):
    id: int
    name: str
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    iata_code: str
    country: str
    country_ru: str | None = None
    country_kk: str | None = None
    country_ky: str | None = None
    region: str | None = None
    cover_photo: str | None = None  # first photo path
    display_order: int = 0

    model_config = {"from_attributes": True}


class DestinationOut(BaseModel):
    id: int
    name: str
    name_ru: str | None = None
    name_kk: str | None = None
    name_ky: str | None = None
    iata_code: str
    country: str
    country_ru: str | None = None
    country_kk: str | None = None
    country_ky: str | None = None
    region: str | None = None
    subtitle: str | None = None
    subtitle_ru: str | None = None
    subtitle_kk: str | None = None
    subtitle_ky: str | None = None
    description: str | None = None
    description_ru: str | None = None
    description_kk: str | None = None
    description_ky: str | None = None
    coords: str | None = None
    timezone: str | None = None
    airport_info: str | None = None
    airport_hint: str | None = None
    currency: str | None = None
    currency_hint: str | None = None
    language_info: str | None = None
    language_hint: str | None = None
    plug_info: str | None = None
    plug_hint: str | None = None
    flight_duration: str | None = None
    display_order: int = 0
    photos: list[DestinationPhotoOut] = []

    model_config = {"from_attributes": True}
