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

weather_api_url = "http://api.weatherapi.com/v1/current.json"

class WeatherApiSensor(Sensor):
    # Subclass the Viam Sensor component and implement the required functions
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "weather-api"), "current")

    def __init__(self, name: str, api_key: str, zipcode: str):
        self.api_key = api_key
        self.zipcode = zipcode
        super().__init__(name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        sensor = cls(config.name, config.attributes.fields["api_key"].string_value, config.attributes.fields["zipcode"].string_value)
        return sensor

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        response = requests.get(''.join([weather_api_url, "?key=", self.api_key, "&q=", self.zipcode]))

        if response.status_code != 200:
            return {"error": f"weatherapi.com didn't return 200, instead got {response.status_code}"}

        return response.json()

    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        raise NotImplemented('do command not supported')

    async def get_geometries(self, *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        raise NotImplemented('get geometries not supported')


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
