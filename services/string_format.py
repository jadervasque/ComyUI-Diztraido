"""Formatacao posicional com expressoes booleanas seguras."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any


class StringFormatError(ValueError):
    """Erro de sintaxe ou referencia em um template de String Format."""


@dataclass(frozen=True)
class _Token:
    kind: str
    value: Any = None


@dataclass
class _ConditionalFrame:
    parent_active: bool
    condition_true: bool
    active: bool
    else_seen: bool = False


_PLACEHOLDER = re.compile(r"\{([1-9]\d*)\}")
_OPTIONAL_LINE_PLACEHOLDER = re.compile(r"\{([1-9]\d*)\?\}")
_BLOCK_DIRECTIVE = re.compile(r"^[ \t]*@(if|else|endif)(?:[ \t]+(.*?))?[ \t]*$")
_TRUE_VALUES = {"true", "1", "yes", "on"}
_FALSE_VALUES = {"false", "0", "no", "off", "", "none", "null"}


def _as_bool(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
    return bool(value)


def _is_empty(value: Any) -> bool:
    """Indica se um valor deve ser considerado vazio em uma linha opcional."""
    return value is None or (isinstance(value, str) and not value.strip())


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _value_at(index: int, values: list[Any]) -> Any:
    if index > len(values):
        raise StringFormatError(f"Input {{{index}}} nao foi fornecido.")
    return values[index - 1]


def _remove_commented_lines(template: str) -> str:
    uncommented = "".join(
        line
        for line in template.splitlines(keepends=True)
        if not line.lstrip(" \t").startswith("#")
    )
    return uncommented.strip("\r\n")


def _tokenize_condition(expression: str, values: list[Any]) -> list[_Token]:
    tokens: list[_Token] = []
    position = 0
    while position < len(expression):
        character = expression[position]
        if character.isspace():
            position += 1
            continue
        if expression.startswith("&&", position):
            tokens.append(_Token("AND"))
            position += 2
            continue
        if expression.startswith("||", position):
            tokens.append(_Token("OR"))
            position += 2
            continue
        comparison = next(
            (
                (symbol, kind)
                for symbol, kind in (
                    ("==", "EQ"),
                    ("!=", "NE"),
                    ("<=", "LE"),
                    (">=", "GE"),
                )
                if expression.startswith(symbol, position)
            ),
            None,
        )
        if comparison:
            symbol, kind = comparison
            tokens.append(_Token(kind))
            position += len(symbol)
            continue
        if character in "<>":
            tokens.append(_Token("LT" if character == "<" else "GT"))
            position += 1
            continue
        if character in "&|!()":
            tokens.append(
                _Token(
                    {
                        "&": "AND",
                        "|": "OR",
                        "!": "NOT",
                        "(": "LPAREN",
                        ")": "RPAREN",
                    }[character]
                )
            )
            position += 1
            continue
        if character == "{":
            match = _PLACEHOLDER.match(expression, position)
            if match is None:
                raise StringFormatError(
                    f"Placeholder invalido na condicao, posicao {position + 1}."
                )
            index = int(match.group(1))
            tokens.append(_Token("VALUE", _value_at(index, values)))
            position = match.end()
            continue

        literal = re.match(r"(?:true|false)\b", expression[position:], re.IGNORECASE)
        if literal:
            tokens.append(_Token("VALUE", literal.group(0).lower() == "true"))
            position += len(literal.group(0))
            continue
        raise StringFormatError(f"Token invalido na condicao, posicao {position + 1}.")

    tokens.append(_Token("END"))
    return tokens


class _ConditionParser:
    def __init__(self, tokens: list[_Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> _Token:
        return self.tokens[self.position]

    def consume(self, kind: str) -> _Token:
        if self.current.kind != kind:
            raise StringFormatError(f"Esperado {kind}, encontrado {self.current.kind}.")
        token = self.current
        self.position += 1
        return token

    def parse(self) -> bool:
        result = self.parse_or()
        if self.current.kind != "END":
            raise StringFormatError("Expressao booleana incompleta.")
        return _as_bool(result)

    def parse_or(self) -> Any:
        result = self.parse_and()
        while self.current.kind == "OR":
            self.consume("OR")
            right = self.parse_and()
            result = _as_bool(result) or _as_bool(right)
        return result

    def parse_and(self) -> Any:
        result = self.parse_comparison()
        while self.current.kind == "AND":
            self.consume("AND")
            right = self.parse_comparison()
            result = _as_bool(result) and _as_bool(right)
        return result

    def parse_comparison(self) -> Any:
        left = self.parse_unary()
        comparison_functions = {
            "EQ": lambda first, second: first == second,
            "NE": lambda first, second: first != second,
            "LT": lambda first, second: first < second,
            "LE": lambda first, second: first <= second,
            "GT": lambda first, second: first > second,
            "GE": lambda first, second: first >= second,
        }
        if self.current.kind not in comparison_functions:
            return left

        operator = self.current.kind
        self.consume(operator)
        right = self.parse_unary()
        try:
            return comparison_functions[operator](left, right)
        except TypeError as error:
            raise StringFormatError(
                "Valores incompativeis para comparacao: "
                f"{type(left).__name__} e {type(right).__name__}."
            ) from error

    def parse_unary(self) -> Any:
        if self.current.kind == "NOT":
            self.consume("NOT")
            return not _as_bool(self.parse_unary())
        if self.current.kind == "LPAREN":
            self.consume("LPAREN")
            result = self.parse_or()
            self.consume("RPAREN")
            return result
        return self.consume("VALUE").value


def _evaluate_condition(expression: str, values: list[Any]) -> bool:
    if not expression.strip():
        raise StringFormatError("A condicao do ternario esta vazia.")
    return _ConditionParser(_tokenize_condition(expression, values)).parse()


def _render_conditional_blocks(template: str, values: list[Any]) -> tuple[str, bool]:
    """Renderiza diretivas @if/@else/@endif de linha inteira, inclusive aninhadas."""
    output: list[str] = []
    frames: list[_ConditionalFrame] = []
    removed_content = False

    for line_number, line in enumerate(template.splitlines(keepends=True), start=1):
        content = line.rstrip("\r\n")
        directive = _BLOCK_DIRECTIVE.fullmatch(content)
        if directive:
            kind, argument = directive.groups()
            if kind == "if":
                if not argument:
                    raise StringFormatError(
                        f"@if on line {line_number} requires a condition."
                    )
                parent_active = frames[-1].active if frames else True
                condition_true = (
                    _evaluate_condition(argument, values) if parent_active else False
                )
                frames.append(
                    _ConditionalFrame(
                        parent_active=parent_active,
                        condition_true=condition_true,
                        active=parent_active and condition_true,
                    )
                )
                continue

            if argument:
                raise StringFormatError(
                    f"@{kind} on line {line_number} does not accept an expression."
                )
            if not frames:
                raise StringFormatError(
                    f"@{kind} on line {line_number} has no matching @if."
                )

            frame = frames[-1]
            if kind == "else":
                if frame.else_seen:
                    raise StringFormatError(
                        f"Duplicate @else for block ending near line {line_number}."
                    )
                frame.else_seen = True
                frame.active = frame.parent_active and not frame.condition_true
                continue

            frames.pop()
            continue

        if not frames or frames[-1].active:
            output.append(line)
        elif content.strip():
            removed_content = True

    if frames:
        raise StringFormatError("Conditional block is missing @endif.")
    return "".join(output), removed_content


def _render_optional_lines(template: str, values: list[Any]) -> tuple[str, bool]:
    """Remove a linha fisica quando qualquer entrada {n?} nela estiver vazia."""
    output: list[str] = []
    removed_line = False

    for line in template.splitlines(keepends=True):
        matches = list(_OPTIONAL_LINE_PLACEHOLDER.finditer(line))
        if not matches:
            output.append(line)
            continue

        indexed_values = [
            (int(match.group(1)), _value_at(int(match.group(1)), values))
            for match in matches
        ]
        if any(_is_empty(value) for _, value in indexed_values):
            removed_line = True
            continue

        output.append(
            _OPTIONAL_LINE_PLACEHOLDER.sub(
                lambda match: _format_value(
                    _value_at(int(match.group(1)), values)
                ),
                line,
            )
        )

    return "".join(output), removed_line


def _find_ternary_end(template: str, start: int) -> int:
    depth = 1
    quote: str | None = None
    escaped = False
    position = start
    while position < len(template):
        character = template[position]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in "\"'":
            quote = character
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return position
        position += 1
    raise StringFormatError("Ternario sem chave de fechamento.")


def _split_ternary(expression: str) -> tuple[str, str, str]:
    quote: str | None = None
    escaped = False
    brace_depth = 0
    paren_depth = 0
    question = None
    colon = None

    for position, character in enumerate(expression):
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in "\"'":
            quote = character
        elif character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth -= 1
        elif character == "(":
            paren_depth += 1
        elif character == ")":
            paren_depth -= 1
        elif (
            character == "?"
            and brace_depth == 0
            and paren_depth == 0
            and question is None
        ):
            question = position
        elif (
            character == ":"
            and brace_depth == 0
            and paren_depth == 0
            and question is not None
        ):
            colon = position
            break

    if question is None or colon is None:
        raise StringFormatError(
            'Ternario deve usar a sintaxe @{condicao?"sim":"nao"}.'
        )
    return (
        expression[:question],
        expression[question + 1 : colon],
        expression[colon + 1 :],
    )


def _parse_branch(branch: str) -> str:
    branch = branch.strip()
    if not branch:
        return ""
    if branch[0] in "\"'":
        try:
            value = ast.literal_eval(branch)
        except (SyntaxError, ValueError) as error:
            raise StringFormatError("Texto invalido em um ramo do ternario.") from error
        if not isinstance(value, str):
            raise StringFormatError("Os ramos do ternario devem ser textos.")
        return value
    return branch


def _render_ternaries(template: str, values: list[Any]) -> str:
    output: list[str] = []
    position = 0
    while position < len(template):
        start = template.find("@{", position)
        if start < 0:
            output.append(template[position:])
            break
        output.append(template[position:start])
        end = _find_ternary_end(template, start + 2)
        condition, true_branch, false_branch = _split_ternary(
            template[start + 2 : end]
        )
        selected = true_branch if _evaluate_condition(condition, values) else false_branch
        output.append(_render_ternaries(_parse_branch(selected), values))
        position = end + 1
    return "".join(output)


def _remove_trailing_structural_commas(text: str) -> str:
    """Remove virgulas antes de chaves/colchetes finais fora de textos entre aspas."""
    output: list[str] = []
    quote: str | None = None
    escaped = False
    position = 0

    while position < len(text):
        character = text[position]
        if quote:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            position += 1
            continue

        if character in "\"'":
            quote = character
            output.append(character)
            position += 1
            continue

        if character == ",":
            lookahead = position + 1
            while lookahead < len(text) and text[lookahead].isspace():
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in "}]":
                position += 1
                continue

        output.append(character)
        position += 1

    return "".join(output)


def _render_template(template: str, values: list[Any]) -> str:
    left_brace = "\u0000DIZTRAIDO_LEFT_BRACE\u0000"
    right_brace = "\u0000DIZTRAIDO_RIGHT_BRACE\u0000"

    rendered, block_removed = _render_conditional_blocks(template, values)
    rendered, optional_removed = _render_optional_lines(rendered, values)
    rendered = _render_ternaries(rendered, values)
    rendered = rendered.replace("{{", left_brace).replace("}}", right_brace)
    rendered = _PLACEHOLDER.sub(
        lambda match: _format_value(_value_at(int(match.group(1)), values)),
        rendered,
    )
    rendered = rendered.replace(left_brace, "{").replace(right_brace, "}")

    if block_removed or optional_removed:
        rendered = _remove_trailing_structural_commas(rendered)
    return rendered


def format_string(
    template: str,
    values: list[Any],
    single_line_output: bool = False,
) -> str:
    """Renderiza placeholders 1-based, linhas opcionais e condicoes booleanas."""
    if not isinstance(template, str):
        raise StringFormatError("O template deve ser uma string.")
    rendered = _render_template(_remove_commented_lines(template), values)
    if single_line_output:
        rendered = re.sub(r"[ \t]*(?:\r\n?|\n)+[ \t]*", " ", rendered)
    return rendered
