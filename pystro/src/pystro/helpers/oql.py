"""
Classes for building IBM Workload Automation Orchestration Query Language
(OQL) query strings from composable parts.

Reference:
https://www.ibm.com/docs/en/workload-automation/10.2.8?topic=reference-using-orchestration-query-language

Grammar supported:
    comparison operators: =, !=, <, <=, >, >=
    IN / NOT IN [v1, v2, ...]
    LIKE / NOT LIKE 'pattern'   (wildcards: @ = any chars, ? = single char)
    AND / OR, with () for grouping, NOT for negation
    ORDER BY field [ASC|DESC], field [ASC|DESC], ...

Example:
    q = (field('jobStreamName') != 'accounting') & (field('totalJobs') > 5)
    q = q | field('jobName').in_(['job1', 'job4'])
    query = OQLQuery(q).order_by('jobName', ('priority', True))
    str(query)
    # "((jobStreamName != 'accounting' AND totalJobs > 5) OR jobName IN ['job1', 'job4']) ORDER BY jobName, priority DESC"
"""

from typing import Optional, Union

OQLValue = Union[str, int, float, bool, None]


def _format_value(value: OQLValue) -> str:
    if isinstance(value, OQLRaw):
        return value.text
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return "'{}'".format(str(value).replace("'", "''"))


class OQLRaw:
    """Wraps a value so it is inserted into the query unquoted, verbatim."""

    def __init__(self, text: str):
        self.text = text


class OQLExpression:
    """Base class for anything that can appear as an OQL filter expression."""

    def render(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.render()

    def __and__(self, other: "OQLExpression") -> "OQLBoolGroup":
        return _combine("AND", self, other)

    def __or__(self, other: "OQLExpression") -> "OQLBoolGroup":
        return _combine("OR", self, other)

    def __invert__(self) -> "OQLNot":
        return OQLNot(self)


def _combine(op: str, left: "OQLExpression", right: "OQLExpression") -> "OQLBoolGroup":
    terms = []
    for term in (left, right):
        if isinstance(term, OQLBoolGroup) and term.op == op:
            terms.extend(term.terms)
        else:
            terms.append(term)
    return OQLBoolGroup(op, terms)


class OQLCondition(OQLExpression):
    """A single `field <op> value` comparison, e.g. `name = 'FOO'`."""

    def __init__(self, field_name: str, operator: str, value: OQLValue):
        self.field_name = field_name
        self.operator = operator
        self.value = value

    def render(self) -> str:
        return f"{self.field_name} {self.operator} {_format_value(self.value)}"


class OQLInCondition(OQLExpression):
    """A `field IN [...]` / `field NOT IN [...]` condition."""

    def __init__(self, field_name: str, values: list[OQLValue], negate: bool = False):
        self.field_name = field_name
        self.values = values
        self.negate = negate

    def render(self) -> str:
        operator = "NOT IN" if self.negate else "IN"
        values = ", ".join(_format_value(v) for v in self.values)
        return f"{self.field_name} {operator} [{values}]"


class OQLLikeCondition(OQLExpression):
    """A `field LIKE 'pattern'` / `field NOT LIKE 'pattern'` condition."""

    def __init__(self, field_name: str, pattern: str, negate: bool = False):
        self.field_name = field_name
        self.pattern = pattern
        self.negate = negate

    def render(self) -> str:
        operator = "NOT LIKE" if self.negate else "LIKE"
        return f"{self.field_name} {operator} {_format_value(self.pattern)}"


class OQLBoolGroup(OQLExpression):
    """An `AND`/`OR` combination of two or more terms."""

    def __init__(self, op: str, terms: list[OQLExpression]):
        self.op = op
        self.terms = terms

    def render(self) -> str:
        parts = []
        for term in self.terms:
            rendered = term.render()
            if isinstance(term, OQLBoolGroup) and term.op != self.op:
                rendered = f"({rendered})"
            parts.append(rendered)
        return f" {self.op} ".join(parts)


class OQLNot(OQLExpression):
    """A `NOT (...)` negation of a term."""

    def __init__(self, term: OQLExpression):
        self.term = term

    def render(self) -> str:
        rendered = self.term.render()
        if isinstance(self.term, OQLBoolGroup):
            rendered = f"({rendered})"
        return f"NOT {rendered}"


class OQLField:
    """
    Reference to a field/attribute name, used to build conditions.

    Supports dotted access for nested fields, e.g. field('dependencies').jobId,
    which is equivalent to field('dependencies.jobId').
    """

    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, sub_field: str) -> "OQLField":
        return OQLField(f"{self.name}.{sub_field}")

    def eq(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, "=", value)

    def ne(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, "!=", value)

    def lt(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, "<", value)

    def le(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, "<=", value)

    def gt(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, ">", value)

    def ge(self, value: OQLValue) -> OQLCondition:
        return OQLCondition(self.name, ">=", value)

    def in_(self, values: list[OQLValue]) -> OQLInCondition:
        return OQLInCondition(self.name, values)

    def not_in(self, values: list[OQLValue]) -> OQLInCondition:
        return OQLInCondition(self.name, values, negate=True)

    def like(self, pattern: str) -> OQLLikeCondition:
        return OQLLikeCondition(self.name, pattern)

    def not_like(self, pattern: str) -> OQLLikeCondition:
        return OQLLikeCondition(self.name, pattern, negate=True)

    def __eq__(self, value: object) -> OQLCondition:  # type: ignore[override]
        return self.eq(value)  # type: ignore[arg-type]

    def __ne__(self, value: object) -> OQLCondition:  # type: ignore[override]
        return self.ne(value)  # type: ignore[arg-type]

    def __lt__(self, value: OQLValue) -> OQLCondition:
        return self.lt(value)

    def __le__(self, value: OQLValue) -> OQLCondition:
        return self.le(value)

    def __gt__(self, value: OQLValue) -> OQLCondition:
        return self.gt(value)

    def __ge__(self, value: OQLValue) -> OQLCondition:
        return self.ge(value)


def field(name: str) -> OQLField:
    return OQLField(name)


def And(*terms: OQLExpression) -> OQLExpression:
    result = terms[0]
    for term in terms[1:]:
        result = result & term
    return result


def Or(*terms: OQLExpression) -> OQLExpression:
    result = terms[0]
    for term in terms[1:]:
        result = result | term
    return result


def Not(term: OQLExpression) -> OQLNot:
    return OQLNot(term)


class OQLOrder:
    """One `field [ASC|DESC]` entry in an ORDER BY clause."""

    def __init__(self, field_name: str, descending: bool = False):
        self.field_name = field_name
        self.descending = descending

    def render(self) -> str:
        return f"{self.field_name} DESC" if self.descending else self.field_name


OQLOrderSpec = Union[str, tuple[str, bool], OQLOrder]


def _to_order(spec: OQLOrderSpec) -> OQLOrder:
    if isinstance(spec, OQLOrder):
        return spec
    if isinstance(spec, tuple):
        field_name, descending = spec
        return OQLOrder(field_name, descending)
    return OQLOrder(spec)


class OQLQuery:
    """
    A full OQL query, combining an optional filter expression with an
    optional ORDER BY clause. Use str(query) to get the OQL string to
    pass as the `oql` API parameter.
    """

    def __init__(self, filter_expr: Optional[OQLExpression] = None, order_by: Optional[list[OQLOrderSpec]] = None):
        self.filter_expr = filter_expr
        self.order_by = [_to_order(spec) for spec in (order_by or [])]

    def filter(self, expr: OQLExpression) -> "OQLQuery":
        self.filter_expr = expr if self.filter_expr is None else self.filter_expr & expr
        return self

    def order(self, *specs: OQLOrderSpec) -> "OQLQuery":
        self.order_by.extend(_to_order(spec) for spec in specs)
        return self

    def render(self) -> str:
        parts = []
        if self.filter_expr is not None:
            parts.append(self.filter_expr.render())
        if self.order_by:
            parts.append("ORDER BY " + ", ".join(o.render() for o in self.order_by))
        return " ".join(parts)

    def __str__(self) -> str:
        return self.render()
