from garmin_daily.snake_to_camel import snake_to_camel, camel_to_upper_snake


def test_snake_to_camel():
    assert snake_to_camel("snake_to_camel") == "snakeToCamel"
    assert snake_to_camel("snake") == "snake"
    assert snake_to_camel("snake__to_camel") == "snakeToCamel"
    assert snake_to_camel("SNAKE_TO") == "snakeTo"


def test_camel_to_upper_snake():
    assert camel_to_upper_snake('camel2Camel2Case') == 'CAMEL2_CAMEL2_CASE'
    assert camel_to_upper_snake('getHTTPResponseCode') == 'GET_HTTP_RESPONSE_CODE'
    assert camel_to_upper_snake('HTTPResponseCodeXYZ') == 'HTTP_RESPONSE_CODE_XYZ'
    assert camel_to_upper_snake('camelCase') == 'CAMEL_CASE'
    assert camel_to_upper_snake('camelCase123') == 'CAMEL_CASE123'
    assert camel_to_upper_snake('CamelCase') == 'CAMEL_CASE'
    assert camel_to_upper_snake('CamelCase123') == 'CAMEL_CASE123'
    assert camel_to_upper_snake('123CamelCase') == '123_CAMEL_CASE'