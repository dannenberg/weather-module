import asyncio
import requests

from typing import Any, ClassVar, Dict, Mapping, Optional
from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

# the rest url we wish to query
weather_api_url = "http://api.weatherapi.com/v1/current.json"

class WeatherApiSensor(Sensor):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "weather-api"), "current")

    def __init__(self, name: str, api_key: str, zipcode: str):
        self.api_key = api_key
        self.zipcode = zipcode
        super().__init__(name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        # parse the args from the config and pass 'em into the constructor for later use.
        sensor = cls(config.name, config.attributes.fields["api_key"].string_value, config.attributes.fields["zipcode"].string_value)
        return sensor

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        # here we build up and submit a GET request, you could rework this to be a POST request if they API you're hitting needs it.
        response = requests.get(''.join([weather_api_url, "?key=", self.api_key, "&q=", self.zipcode]))

        # return the status code as an error if we dont get a 200 OK back.
        if response.status_code != 200:
            return {"error": f"weatherapi.com didn't return 200, instead got {response.status_code}"}

        # this would be a great place to modify the data returned if the format direct from the API isn't to your liking.
        return response.json()


async def main():
    """This function creates and starts a new module, after adding all desired resource models.
    Resource creators must be registered to the resource registry before the module adds the resource model.
    """
    Registry.register_resource_creator(Sensor.SUBTYPE, WeatherApiSensor.MODEL, ResourceCreatorRegistration(WeatherApiSensor.new))

    module = Module.from_args()
    module.add_model_from_registry(Sensor.SUBTYPE, WeatherApiSensor.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
