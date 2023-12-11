import ast
import builtins
import os
import re
import shutil
from custom_components.pyscript.const import FOLDER
from custom_components.pyscript.state import STATE_VIRTUAL_ATTRS

from homeassistant.core import split_entity_id
from homeassistant.helpers import service as ha_service
from homeassistant.helpers.entity_registry import EntityRegistry

from .loader import *


class Generator:
    BASE_ENTITYCLASS_NAME = "_entity"
    ENTITY_SUFFIX = "_entity"
    DOCSTRING_INDENT = " " * 8

    def __init__(self, include_regexes, exclude_regexes):
        self.include_regexes = include_regexes
        self.exclude_regexes = exclude_regexes

        self.domains = {}
        self.domain_entity_methods = {}
        self.domain_attributes = {}
        self.invalid_identifiers = []

    @pyscript_compile()
    def skip(self, fqn):
        if not self.include_regexes or any(regex.search(fqn) for regex in self.include_regexes):
            if not any(regex.search(fqn) for regex in self.exclude_regexes):
                return False
        return True

    def get_or_create_cls(self, domain_id: str, base_class: str = "") -> ast.ClassDef:
        domain = self.domains.get(domain_id)
        if domain is None:
            domain = ast.ClassDef(name=domain_id, bases=[], keywords=[], body=[], decorator_list=[])
            if base_class:
                domain.bases.append(ast.Name(id=base_class))
            self.domains[domain_id] = domain
        return domain

    def create_service(self, domain_id, service_id, service):
        docstring = "\n" + self.DOCSTRING_INDENT
        docstring += service["description"]
        docstring += "\n" + self.DOCSTRING_INDENT

        arg_list = []
        arg_option_list = []
        default_list = []

        if "fields" in service:
            for field_name, field in service["fields"].items():
                description = field.get("description")
                if description is not None:
                    docstring += f":param {field_name}: {description}\n{self.DOCSTRING_INDENT}"

                arg_annotation = None
                default_value = None

                # TODO check documentation for multiple selectors
                for selector_id, selector in field.get("selector", {}).items():
                    if selector_id == "number":
                        # TODO add min, max... to docstring
                        is_float = False
                        if "step" in selector:
                            is_float = isinstance(selector["step"], float) or selector["step"] == "any"

                        arg_annotation = ast.Name(id="float" if is_float else "int")
                        default_value = 0
                    elif selector_id == "boolean":
                        arg_annotation = ast.Name(id="bool")
                        default_value = False
                    elif selector_id in ("text", "date", "datetime", "time"):
                        arg_annotation = ast.Name(id="str")
                        default_value = ""
                    elif selector_id == "select":
                        default_value = ""

                        options = selector.get("options")
                        elts = [ast.Constant(value="")]
                        for option in options:
                            if isinstance(option, dict):
                                elts.append(ast.Constant(value=option["value"]))
                            else:
                                elts.append(ast.Constant(value=option))

                        arg_annotation = ast.Subscript(
                            value=ast.Name(id="Literal"),
                            slice=ast.Index(value=ast.Tuple(elts=elts)),
                        )
                        # TODO add options to docstring
                    # else config_entry | object | entity

                ast_arg = ast.arg(arg=field_name, annotation=arg_annotation)

                if "required" in field and field["required"] is True:
                    arg_list.append(ast_arg)
                else:
                    arg_option_list.append(ast_arg)
                    default_list.append(ast.Constant(default_value))

        service_args = ast.arguments(
            args=arg_list + arg_option_list,
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=default_list,
        )

        returns = None
        if "response" in service:
            returns = ast.Subscript(
                value=ast.Name(id="dict"),
                slice=ast.Index(value=ast.Tuple(elts=[ast.Name(id="str"), ast.Name(id="Any")])),
            )

        target = service.get("target")

        # create entity method
        if target is not None:
            entity_cls = f"{domain_id}{self.ENTITY_SUFFIX}"
            if entity_cls in self.domains:
                entity_args = ast.arguments(
                    args=[ast.arg(arg="self")] + arg_list + arg_option_list,
                    posonlyargs=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=default_list,
                )

                if len(entity_args.args) > 1:
                    entity_args.args.insert(1, ast.arg(arg="*"))
                ast_func = ast.FunctionDef(
                    name=service_id,
                    args=entity_args,
                    body=[ast.Expr(value=ast.Constant(value=docstring)), ast.Expr(ast.Ellipsis())],
                    decorator_list=[],
                    returns=returns,
                )
                self.get_or_create_cls(entity_cls).body.append(ast_func)

            service_args.args.insert(0, ast.arg(arg="entity_id", annotation=ast.Name(id="str")))

        if len(service_args.args) > 0:
            service_args.args.insert(0, ast.arg(arg="*"))

        ast_func = ast.FunctionDef(
            name=service_id,
            args=service_args,
            body=[ast.Expr(value=ast.Constant(value=docstring)), ast.Expr(ast.Ellipsis())],
            decorator_list=[[ast.Name(id="staticmethod")]],
            returns=returns,
        )
        self.get_or_create_cls(domain_id).body.append(ast_func)

    def generate_services(self):
        descriptions = ha_service.async_get_all_descriptions(hass)
        for domain_id, services in descriptions.items():  # type: ignore
            for service_id, service in services.items():
                fqn = f"{domain_id}.{service_id}"
                if self.skip(fqn):
                    continue
                try:
                    if not service_id.isidentifier():
                        self.invalid_identifiers.append(fqn)
                        log.warning(f"Invalid python identifier {fqn}")
                        continue
                    self.create_service(domain_id, service_id, service)
                except Exception as e:
                    log.error(f"Failed to generate function for {fqn} {service}")
                    raise e

    def collect_atts(self, domain_id, entity_id):
        state = hass.states.get(f"{domain_id}.{entity_id}")
        if state is None:
            return
        entity_attributes = self.domain_attributes.setdefault(f"{domain_id}{self.ENTITY_SUFFIX}", set())
        for attr in state.attributes.keys():
            fqn = f"{domain_id}.{entity_id}.{attr}"
            if self.skip(fqn):
                continue
            if not attr.isidentifier():
                self.invalid_identifiers.append(fqn)
                log.warning(f"Invalid python identifier {fqn}")
                continue
            entity_attributes.add(attr)

    def generate_entities(self):
        er = hass.data["entity_registry"]  # type: EntityRegistry

        for entity in er.entities.values():
            try:
                if entity.disabled or entity.hidden:
                    continue
                if self.skip(entity.entity_id):
                    continue

                domain_id, entity_id = split_entity_id(entity.entity_id)

                if not entity_id.isidentifier():
                    self.invalid_identifiers.append(entity.entity_id)
                    log.warning(f"Invalid python identifier {entity.entity_id}")
                    continue

                self.collect_atts(domain_id, entity_id)

                self.get_or_create_cls(domain_id).body.append(
                    ast.Assign(
                        targets=[ast.Name(id=entity_id)],
                        value=ast.Call(
                            ast.Name(id=f"{domain_id}{self.ENTITY_SUFFIX}"), args=[], keywords=[]
                        ),
                    )
                )

                self.get_or_create_cls(domain_id + self.ENTITY_SUFFIX, self.BASE_ENTITYCLASS_NAME)
            except Exception as e:
                log.error(f"Failed to generate sensor for {entity}")
                raise e

    def create_base_entity_class(self):
        cls = ast.ClassDef(
            name=self.BASE_ENTITYCLASS_NAME, bases=[], keywords=[], body=[], decorator_list=[]
        )
        for attr in STATE_VIRTUAL_ATTRS:
            cls.body.append(ast.AnnAssign(target=ast.Name(id=attr), annotation=ast.Name(id="Any"), simple=1))
        return cls

    def generate(self):
        body = []
        body.append(
            ast.ImportFrom(
                module="typing",
                names=[
                    ast.alias(name="Any", asname=None),
                    ast.alias(name="Literal", asname=None),
                ],
            )
        )
        body.append(self.create_base_entity_class())

        self.generate_entities()
        self.generate_services()

        sorted_domains = sorted(
            self.domains.keys(),
            key=lambda x: (x.split("_")[0], "" if "_entity" in x else "z"),
        )

        for domain_id in sorted_domains:
            domain = self.domains[domain_id]
            attributes = self.domain_attributes.get(domain_id)
            if attributes is not None:
                for attr in sorted(attributes, reverse=True):
                    domain.body.insert(
                        0,
                        ast.AnnAssign(
                            target=ast.Name(id=attr, ctx=ast.Store()),
                            annotation=ast.Name(id="Any", ctx=ast.Load()),
                            value=None,
                            simple=1,
                        ),
                    )

            if len(domain.body) == 0:
                # empty class body
                domain.body.append(ast.Expr(ast.Ellipsis()))

            body.append(domain)

        module = ast.Module(body=body, type_ignores=[])
        code = ast.unparse(ast.fix_missing_locations(module))
        return code


@service(supports_response="only")
def autocomplete_generator():
    """
    https://github.com/dmamelin/pyscript_autocomplete
    """
    try:
        """pyscript error. If config empty pyscript.app_config doesn't exist"""
        cfg = pyscript.app_config
    except:
        cfg = {}

    result = {}

    module_name = "pyscript_mock"

    error_list = []

    empty_module = hass.config.path(FOLDER + f"/modules/{module_name}.py")
    if not os.path.exists(empty_module):
        error_list.append(f"{empty_module} does not exists")

    target_path = cfg.get("target_path")
    if not target_path:
        target_path = hass.config.path(FOLDER + f"/{module_name}/")
    if not os.access(target_path, os.W_OK):
        error_list.append(f"{target_path} does not exist or is not writable")

    include = cfg.get("include") or []
    include_regexes = []
    for pattern in include:
        include_regexes.append(re.compile(pattern))

    exclude = cfg.get("exclude") or []
    exclude_regexes = []
    for pattern in exclude:
        exclude_regexes.append(re.compile(pattern))

    if len(error_list) == 0:
        generator_path = hass.config.path(FOLDER + "/" + pyscript.get_global_ctx().replace(".", "/") + "/")
        shutil.copy(f"{generator_path}/mock_init.tpl", target_path + "__init__.py")
        shutil.copy(f"{generator_path}/pyscript_builtins.py", target_path)

        generator = Generator(include_regexes, exclude_regexes)
        code = generator.generate()
        with builtins.open(target_path + "/pyscript_generated.py", "w", encoding="utf-8") as f:
            f.write("# fmt:off\n")
            f.write(code)
            f.close()
        result["info"] = f"{len(generator.domains)} classes"
        if generator.invalid_identifiers:
            result["invalid_identifiers"] = generator.invalid_identifiers

    if error_list:
        result["errors"] = error_list

    return result
