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
