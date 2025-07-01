import pytest
from garmin_daily.columns_mapper import ColumnsMapper, GarminCol


def test_columns_mapper_row_columns(header_row):
    mapper = ColumnsMapper(header_row[0])
    assert mapper.row_columns == header_row[1]["row_columns"]


def test_columns_mapper_map(header_row):
    fields = {
        GarminCol.DATE: "-date-",
        GarminCol.DURATION: "-duration-",
    }
    mapper = ColumnsMapper(header_row[0])
    assert mapper.map(fields) == header_row[1]["row"]


def test_columns_mapper_idx(header_row):
    mapper = ColumnsMapper(header_row[0])
    for column in [GarminCol.DISTANCE, GarminCol.DATE, GarminCol.STEPS]:
        assert mapper.idx(column) == header_row[1]["idx"][column]


def test_missing_column_error():
    """Test that a helpful error is raised when required column is missing."""
    # Create a header row that's missing the DATE column
    header_row = ["location", "sport", "duration", "distance", "steps"]

    mapper = ColumnsMapper(header_row)

    # Test __getitem__ method
    with pytest.raises(ValueError) as exc_info:
        mapper[GarminCol.DATE]

    error_str = str(exc_info.value)
    assert "Required column 'DATE' not found" in error_str
    assert "Missing columns:" in error_str
    assert "Expected header names:" in error_str
    assert "date" in error_str.lower()

    # Test idx method
    with pytest.raises(ValueError) as exc_info:
        mapper.idx(GarminCol.DATE)

    error_str = str(exc_info.value)
    assert "Required column 'DATE' not found" in error_str
    assert "Missing columns:" in error_str
    assert "Expected header names:" in error_str
    assert "date" in error_str.lower()
