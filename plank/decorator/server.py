from typing import Callable, Any
from plank.server.api import CommonAPI, CallableAPI
from plank.utils.function import can_bound


def api(end_point: Callable[[Any], Any]):
    assert isinstance(end_point, Callable), f"The `end_point` of routable should be Callable, unexpected with {type(end_point)}"
    if can_bound(end_point):
        return CommonAPI(end_point)
    else:
        return CallableAPI(end_point)