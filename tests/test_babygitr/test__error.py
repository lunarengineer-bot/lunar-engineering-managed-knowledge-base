"""Tests exceptions raised in BabyGitr.

This tests that each exception created in BabyGitr functions appropriately.
"""
import pytest
from babygitr import _error as b_e

exception_list = [b_e.BabyGitrBaseException]
message_heads = ["BabyGitrBaseException"]


@pytest.mark.parametrize(("exception"), exception_list)
def test_BabyGitrExceptions(exception: b_e.BabyGitrBaseException):
    with pytest.raises(exception):
        raise exception


@pytest.mark.parametrize(("exception", "msg_head"), zip(exception_list, message_heads))
def test_BabyGitrExceptions_with_message(
    exception: b_e.BabyGitrBaseException, msg_head: str
):
    with pytest.raises(exception):
        raise exception
    with pytest.raises(exception, match=msg_head):
        raise exception()
    with pytest.raises(exception, match="steve"):
        raise exception("steve")
