from garmin_daily.mappers import ActivityMapper


def test_activity_mapper():
    # Test basic activity name mapping
    mapper = ActivityMapper([("trail", "Roller skiing"), ("running", "Jogging")])
    assert mapper.get_activity_name("trail run") == "Roller skiing"
    assert mapper.get_activity_name("running") == "Jogging"
    assert mapper.get_activity_name("swimming") == "swimming"

    # Test case insensitivity
    mapper = ActivityMapper([("TrAiL", "Roller skiing")])
    assert mapper.get_activity_name("Trail Run") == "Roller skiing"
    assert mapper.get_activity_name("TRAIL") == "Roller skiing"


def test_activity_mapper_empty():
    # Test empty mappings
    mapper = ActivityMapper([])
    assert mapper.get_activity_name("any activity") == "any activity"


def test_activity_mapper_pattern_matching():
    # Test pattern matching with regex
    mapper = ActivityMapper(
        [(r"run.*park", "Park Run"), (r"cycle|bike", "Cycling"), (r"swim.*pool", "Pool Swimming")]
    )

    assert mapper.get_activity_name("run in park") == "Park Run"
    assert mapper.get_activity_name("running through park") == "Park Run"
    assert mapper.get_activity_name("cycle training") == "Cycling"
    assert mapper.get_activity_name("bike ride") == "Cycling"
    assert mapper.get_activity_name("swimming in pool") == "Pool Swimming"
    assert mapper.get_activity_name("just swimming") == "just swimming"
