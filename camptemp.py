import html
import urllib.request
import json

from mautrix.types import TextMessageEventContent
from maubot import Plugin, MessageEvent
from maubot.handlers import command


API_URL="https://wetter.poempelfox.de/api/getlastvalue/"
SENSORS=[
    ("Temperatur", "°C", 74),
    ("Luftfeuchtigkeit", "%", 75),
    ("Luftdruck", " hPa", 76),
    ("Windrichtung", "°", 78),
    ("Windgeschwindigkeit", " m/s", 79),
    ("Niederschlag", " mm/min", 81),
    ("Feinstaub (µg/m³)", "", [
        ("PM1.0", "", 82),
        ("PM2.5", "", 83),
        ("PM4.5", "", 84),
        ("PM10.5", "", 85)
    ]),
    ("Beleuchtungsstärke", "lux", 87),
]


class CampTempBot(Plugin):
    @classmethod
    def get_sensor(cls, sensorid: int) -> str:
        url = API_URL + str(sensorid)
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        if data is None:
            return None
        value = data['v']
        return value

    @command.new("temp", help="")
    @command.argument("message", pass_raw=True, required=False)
    async def temp_handler(self, evt: MessageEvent, message: str) -> None:
        content = ""
        for (label, unit, sensorid) in SENSORS:
            subcontent = ""
            if type(sensorid) is list:
                for (sublabel, subunit, subsensorid) in sensorid:
                    subvalue = self.get_sensor(subsensorid)
                    if subvalue:
                        if subcontent == "":
                            subcontent = f"{label} "
                        else:
                            subcontent += ", "
                        subcontent += f"{sublabel} {subvalue}{subunit}"
            else:
                value = self.get_sensor(sensorid)
                if value is not None:
                    subcontent = f"{label} {value}{unit}"
            if subcontent != "":
                if content != "":
                    content += "; "
                content += subcontent
        await evt.respond(content)
