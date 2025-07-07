import pytest
from dictator.utilities import generate_sha1, generate_login_key


@pytest.mark.parametrize(
    "input,output",
    [
        ("Colin-9391", "81738c861dc8790379ac3e400aa7b5d5df7938a5"),
        ("TanyaB-2264", "22858ea80d0b927a6757218fae91d8cd65a6f80b"),
    ],
)
def test_generate_sha1(input, output):
    assert generate_sha1(input) == output


def test_generate_login_key():
    # F93V7-GVD69-UERJF-7WTTE
    login_key = generate_login_key()
    assert len(login_key) == 23
