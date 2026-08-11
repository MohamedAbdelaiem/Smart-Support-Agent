import jsonschema


def validate_tool_args(call_input: dict, schema: dict) -> tuple[bool, str]:
    """Validates tool input arguments against a JSON schema."""
    try:
        jsonschema.validate(instance=call_input, schema=schema)
        return True, ""
    except jsonschema.ValidationError as e:
        return False, str(e)