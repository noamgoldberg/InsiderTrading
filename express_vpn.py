from typing import Optional, Union, Dict
from evpn import ExpressVpnApi
import random


def is_express_vpn_activated() -> bool:
    with ExpressVpnApi() as api:
        return api.get_status().get("info", {}).get("activated", False)

def is_express_vpn_connected() -> bool:
    with ExpressVpnApi() as api:
        return api.get_status().get("info", {}).get("connected", False)

def _establish_location(
    location: Optional[str] = "random",
    _id: Optional[Union[str, int]] = None,
) -> Dict[str, str]:
    with ExpressVpnApi() as api:
        location_dicts = api.locations
        location_names = [loc["name"] for loc in location_dicts]
        if location == "random":
            location = random.choice(location_names)
        elif location is None:
            location = "United States"
        location = location.title()
        if location not in ["random"] and location not in location_names:
            raise ValueError(f"{location}: Location invalid; choose from {['random'] + location_names}")
        matching_dicts = [
            loc_dict for loc_dict in location_dicts
            if loc_dict["name"].title() == location
            or loc_dict["country_code"].title() == location
        ]
        _id = _id if str(_id).isdigit() else random.choice(matching_dicts)["id"]
        matching_dicts = [
            loc_dict for loc_dict in matching_dicts
            if loc_dict["id"] == _id
        ]
        if len(matching_dicts) == 0:
            raise ValueError(f"No address for location '{location}' with id '{_id}'")
        elif len(matching_dicts) > 1:
            raise ValueError(f"Multiple addresses for location '{location}' with id '{_id}': {matching_dicts}")
        return matching_dicts[0]

def connect_vpn(
    location: Optional[str] = "random",
    _id: Optional[Union[str, int]] = None,
) -> None:
    if not is_express_vpn_activated():
        raise Exception("Express VPN not yet activated; must activate (with activation code) in order to use API")
    with ExpressVpnApi() as api:
        location_dict = _establish_location(location=location, _id=_id)
        print(f"Connecting to: {location_dict['name']} ({location_dict['country_code']})")
        api.connect(location_dict["id"])