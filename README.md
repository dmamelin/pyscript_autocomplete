
# Home Assistant PyScript Autocomplete
This **experimental** project offers a solution to enhance PyScript script development for Home Assistant by providing autocomplete functionality in development environments. 


## Features
- **PyScript Objects Mocking**: Enhances autocomplete for PyScript objects in IDEs.
- **Class Generation for Services**: Auto-generates Python classes for Home Assistant services, including methods and documentation.
- **Sensor Class Generation**:  Creates classes for Home Assistant sensors with relevant attributes.
- **Method Generation For Sensors**: Supports `sensor.method()` generation for service calls with [target](https://developers.home-assistant.io/docs/dev_101_services/#service-descriptions)
- **IDE-Only Operation**: Operates exclusively within IDEs, not affecting PyScript or Home Assistant functionality.
    ![image](https://github.com/custom-components/pyscript/assets/22717990/4820f2ed-c9b8-4372-b167-8c3bed38dc3e)



## Installation
- **Create Mock File**: In the `pyscript/modules/` directory, create an empty file named `pyscript_mock.py`.
- **Update PyScript Configuration**: Enable `allow_all_imports` and `hass_is_global` in your PyScript [configuration](https://github.com/custom-components/pyscript#configuration)
- **Configure PyScript**: Add the following to your PyScript configuration in `configuration.yaml`
    - add to pyscript configuration
    ```yaml
    apps:
        pyscript_autocomplete:
    ```
    - Copy the `apps/pyscript_autocomplete` folder to your PyScript directory.
- **Generate Autocomplete Data**: Use the Home Assistant UI to call the `pyscript.autocomplete_generator` service.
- **Integrate with Local Project**: Copy the `pyscript_mock` directory from your PyScript directory to your local project directory.
- **Import in PyScript Files**: In any PyScript file, add the line `from pyscript_mock import *` for autocomplete functionality.

## Advanced Configuration

- `target_path:` Specifies the directory for writing generated files. The default is `pyscript/pyscript_mock/`.
- `exclude:` A list of regular expressions used to exclude specific services, sensors, and attributes. By default, this list is empty, meaning nothing is excluded.
- `include:` A list of regular expressions to specifically include certain services, sensors, and attributes. By default, all are included.

Example:
```yaml
apps:
  pyscript_autocomplete:
    target_path: /tmp/pyscript_mock/
    exclude:
        - person\.test\.friendly_name
    include:
        - sensor\.
        - homeassistant\.turn_.*
        - person

```

## Notes
- Incompatibility with identifiers that are invalid in Python (e.g., starting with a number).
- Use only `from pyscript_mock import *`. Importing specific classes will lead to errors, as these classes do not exist in PyScript runtime.
- In PyScript runtime, `sensor.some_sensor_id` becomes a `StateVal` state object, representing the current value of the sensor.
    ```python
    # This code will not work
    @state_trigger(sensor.some_sensor_id)
    def test(context: Context, var_name: str, value: str, **kwargs):
    # Correct code
    @state_trigger("sensor.some_sensor_id")
    def test(context: Context, var_name: str, value: str, **kwargs):
    ```
    - If https://github.com/custom-components/pyscript/pull/555 is accepted, it will be possible to use:
        ```python
        @state_trigger(sensor.some_sensor_id.entity_id)
        @state_trigger(f"{sensor.some_sensor_id.entity_id}>10")
        def test(context: Context, var_name: str, value: str, **kwargs):
        ```