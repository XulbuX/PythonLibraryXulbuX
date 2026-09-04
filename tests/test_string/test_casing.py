import xulbux.string as _string_module


def test_decompose_standard_casing() -> None:
    assert _string_module.decompose("camelCaseString") == ["camel", "case", "string"]
    assert _string_module.decompose("PascalCaseString") == ["pascal", "case", "string"]
    assert _string_module.decompose("snake_case_string") == ["snake", "case", "string"]
    assert _string_module.decompose("kebab-case-string") == ["kebab", "case", "string"]
    assert _string_module.decompose("SCREAMING_SNAKE_CASE") == ["screaming", "snake", "case"]
    assert _string_module.decompose("mixed_Case-StringExample") == ["mixed", "case", "string", "example"]
    assert _string_module.decompose("singleword") == ["singleword"]
    assert _string_module.decompose("myHTTPServer_port-config") == ["my", "http", "server", "port", "config"]
    assert _string_module.decompose("getHTTPResponse") == ["get", "http", "response"]
    assert _string_module.decompose("HTTPServer") == ["http", "server"]


def test_decompose_with_custom_separators_and_lower_all() -> None:
    assert _string_module.decompose("version2_0", seps="_.") == ["version2", "0"]
    assert _string_module.decompose("PascalCase", lower_all=False) == ["Pascal", "Case"]
    assert _string_module.decompose("snake_case", lower_all=False) == ["snake", "case"]
    assert _string_module.decompose("mixed_Case", lower_all=False) == ["mixed", "Case"]
    assert _string_module.decompose("myHTTPServer.port", seps=".", lower_all=False) == ["my", "HTTP", "Server", "port"]


def test_to_camel_case_upper_and_lower() -> None:
    assert _string_module.to_camel_case("snake_case_string") == "SnakeCaseString"
    assert _string_module.to_camel_case("kebab-case-string") == "KebabCaseString"
    assert _string_module.to_camel_case("PascalCaseString") == "PascalCaseString"
    assert _string_module.to_camel_case("camelCaseString") == "CamelCaseString"
    assert _string_module.to_camel_case("SCREAMING_SNAKE_CASE") == "ScreamingSnakeCase"
    assert _string_module.to_camel_case("single") == "Single"

    assert _string_module.to_camel_case("snake_case_string", upper=False) == "snakeCaseString"
    assert _string_module.to_camel_case("kebab-case-string", upper=False) == "kebabCaseString"
    assert _string_module.to_camel_case("PascalCaseString", upper=False) == "pascalCaseString"
    assert _string_module.to_camel_case("camelCaseString", upper=False) == "camelCaseString"
    assert _string_module.to_camel_case("SCREAMING_SNAKE_CASE", upper=False) == "screamingSnakeCase"
    assert _string_module.to_camel_case("single", upper=False) == "single"


def test_to_delimited_case_formats() -> None:
    assert _string_module.to_delimited_case("camelCaseString") == "camel_case_string"
    assert _string_module.to_delimited_case("PascalCaseString") == "pascal_case_string"
    assert _string_module.to_delimited_case("snake_case_string") == "snake_case_string"
    assert _string_module.to_delimited_case("kebab-case-string") == "kebab_case_string"
    assert _string_module.to_delimited_case("SCREAMING_SNAKE_CASE") == "screaming_snake_case"
    assert _string_module.to_delimited_case("single") == "single"

    assert _string_module.to_delimited_case("camelCaseString", delimiter="-") == "camel-case-string"
    assert _string_module.to_delimited_case("PascalCaseString", delimiter=".") == "pascal.case.string"

    assert _string_module.to_delimited_case("camelCaseString", screaming=True) == "CAMEL_CASE_STRING"
    assert _string_module.to_delimited_case("PascalCaseString", screaming=True) == "PASCAL_CASE_STRING"
    assert _string_module.to_delimited_case("camelCaseString", delimiter="-", screaming=True) == "CAMEL-CASE-STRING"
