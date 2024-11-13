from best_shot.types import Shot, dump_io_value, id_io_value, is_io_value


def test_is_io_value():
    assert is_io_value("test") is True
    assert is_io_value({"key": "value"}) is True
    assert is_io_value(123) is False
    assert is_io_value(["test"]) is False


def test_data_key():
    data = {"b": 2, "a": 1}
    assert dump_io_value(data) == '{"a":1,"b":2}'


def test_data_hash():
    data = {"test": "value"}
    expected_hash = "f98be16ebfa861cb39a61faff9e52b33f5bcc16bb6ae72e728d226dc07093932"
    assert id_io_value(data) == expected_hash


def test_init_with_id():
    shot = Shot({"input": "test"}, {"output": "result"}, "test_id")
    assert shot.inputs == {"input": "test"}
    assert shot.outputs == {"output": "result"}
    assert shot.id == "test_id"


def test_init_without_id():
    inputs = {"input": "test"}
    shot = Shot(inputs, {"output": "result"})
    assert shot.id == id_io_value(inputs)


def test_key_property():
    inputs = {"input": "test"}
    shot = Shot(inputs, {"output": "result"})
    assert shot.key == dump_io_value(inputs)
