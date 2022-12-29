from garmin_daily.snake_to_camel import snake_to_camel


def test_snake_to_camel():
    assert snake_to_camel("snake_to_camel") == "snakeToCamel"
    assert snake_to_camel("snake") == "snake"
    assert snake_to_camel("snake__to_camel") == "snakeToCamel"
    assert snake_to_camel("SNAKE_TO") == "snakeTo"
