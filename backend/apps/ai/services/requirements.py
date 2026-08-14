from dataclasses import dataclass, field, asdict


@dataclass
class PlaceRequirements:
    district: str | None = None
    noise: str | None = None
    wifi_min: int | None = None
    sockets: bool | None = None
    max_price: int | None = None
    duration_hours: int | None = None
    free_now: bool | None = None
    query_text: str = ""

    def to_dict(self):
        data = asdict(self)
        return data

    def __str__(self):
        parts = []
        if self.district:
            parts.append(f"tuman={self.district}")
        if self.noise:
            parts.append(f"shovqin={self.noise}")
        if self.wifi_min is not None:
            parts.append(f"wifi>={self.wifi_min}")
        if self.sockets is not None:
            parts.append(f"rozetka={self.sockets}")
        if self.max_price is not None:
            parts.append(f"narx<={self.max_price}")
        if self.duration_hours:
            parts.append(f"davomiylik={self.duration_hours} soat")
        if self.free_now:
            parts.append("hozir bo'sh")
        return ", ".join(parts) or "hech qanday talab"