from pathlib import Path
import pytest

from software.archiver import archive_with_date


def test_archive_with_date_dashed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = Path("report_2023-09-15.csv")
    src.write_text("data")

    dest = archive_with_date(src)

    expected = Path("archive") / "2023-09-15" / src.name
    assert dest == expected
    assert dest.exists()
    assert not src.exists()


def test_archive_with_date_compact(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = Path("report_20230915.csv")
    src.write_text("data")

    dest = archive_with_date(src)
    expected = Path("archive") / "20230915" / src.name
    assert dest == expected
    assert dest.exists()


def test_archive_with_date_no_match(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src = Path("report.csv")
    src.write_text("data")

    with pytest.raises(ValueError):
        archive_with_date(src)
    assert src.exists()
