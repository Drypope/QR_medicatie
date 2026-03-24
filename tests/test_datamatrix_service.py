import pytest

from app.services.datamatrix_service import render_data_matrix_png


def test_render_data_matrix_returns_png_bytes():
    try:
        result = render_data_matrix_png("A1:1|B1:2")
    except RuntimeError:
        pytest.skip("libdmtx shared library unavailable in test environment")
    assert result[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_data_matrix_empty_payload_raises():
    with pytest.raises(ValueError):
        render_data_matrix_png("")
