from dictator.utilities import sanitise_username


def test_sanitise_username():
    assert sanitise_username("normalname") == "normalname"
    assert sanitise_username("name_with_underscore") == "name-with-underscore"
    assert sanitise_username("name.with.dot") == "name-with-dot"
    assert sanitise_username("invalid!@#chars") == "invalidchars"
    assert sanitise_username("mixed_.name!123") == "mixed--name123"
    assert sanitise_username("a" * 40) == "a" * 32
    assert sanitise_username("_.!@#") == "--"
