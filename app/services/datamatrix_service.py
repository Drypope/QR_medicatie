from io import BytesIO

from PIL import Image


def render_data_matrix_png(payload: str, scale: int = 5) -> bytes:
    if not payload:
        raise ValueError("Cannot render Data Matrix for empty payload")

    try:
        from pylibdmtx.pylibdmtx import encode
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Data Matrix encoder dependency is unavailable") from exc

    encoded = encode(payload.encode("utf-8"))
    image = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    resized = image.resize((encoded.width * scale, encoded.height * scale), Image.NEAREST)
    output = BytesIO()
    resized.save(output, format="PNG")
    return output.getvalue()
