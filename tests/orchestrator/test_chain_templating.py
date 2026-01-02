from jinja2 import Template


def test_basic_rendering():
    """Verify basic variable substitution."""
    template = "Hello {{ name }}!"
    context = {"name": "World"}
    result = Template(template).render(**context)
    assert result == "Hello World!"


def test_multiple_variables():
    """Verify multiple variables."""
    template = "{{ greeting }} {{ name }}!"
    context = {"greeting": "Hi", "name": "User"}
    result = Template(template).render(**context)
    assert result == "Hi User!"


def test_missing_variable():
    """Verify behavior with missing variables (Jinja2 defaults to empty string)."""
    template = "Hello {{ name }}!"
    context = {}
    result = Template(template).render(**context)
    assert result == "Hello !"


def test_complex_object():
    """Verify object attribute access."""

    class User:
        def __init__(self, name):
            self.name = name

    template = "User: {{ user.name }}"
    context = {"user": User("Alice")}
    result = Template(template).render(**context)
    assert result == "User: Alice"
