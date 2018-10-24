from __future__ import annotations
from contextlib import contextmanager
from typing import Sequence, Mapping, Generator, Union, Tuple, List
import operator
from dataclasses import dataclass
import enum
from collections import deque
import copy


class WriteOutError(ValueError):
    pass


class Indent(enum.Enum):
    dedent = enum.auto()
    nothing = enum.auto()
    indent = enum.auto()

    @staticmethod
    def from_int(val: int) -> Indent:
        if val > 0:
            return Indent.indent
        elif val < 0:
            return Indent.dedent
        else:
            return Indent.nothing

    def to_int(self) -> int:
        if self is Indent.indent:
            return 1
        elif self is Indent.dedent:
            return -1
        else:
            return 0

    def __add__(self, other: Indent) -> Indent:
        if type(other) is Indent:
            return Indent.from_int(self.to_int() + other.to_int())
        return NotImplemented


@dataclass
class _HtmlLine:
    line: str
    indent: Indent


class Html:
    def __init__(
            self,
            content: Union[str, Sequence[str]] = None,
    ) -> None:
        if content is None:
            contents: List[_HtmlLine] = []
        elif isinstance(content, str):
            contents = [_HtmlLine(line=content, indent=Indent.nothing)]
        else:
            contents = [_HtmlLine(line=line, indent=Indent.nothing) for line in content]
        self._inner_html = deque(contents)
        self._buffer = ''

    @contextmanager
    def tag(
            self,
            name: str,
            id_: str = None,
            classes: Sequence[str] = None,
            styles: Mapping[str, str] = None,
            attributes: Mapping[str, str] = None,
    ) -> Generator[Html, None, None]:
        open_tag, close_tag = Html._get_open_and_close_tags(
            name, id_, classes, styles, attributes
        )
        self.newline()
        operator.iadd(self, open_tag)
        self.newline(indent=Indent.indent)
        try:
            yield self
        finally:
            self.newline(indent=Indent.dedent)
            operator.iadd(self, close_tag)
            self.newline()

    def enclose_with_tag(
            self,
            *tag_args,
            **tag_attributes
    ) -> None:
        open_tag, close_tag = Html._get_open_and_close_tags(*tag_args, **tag_attributes)
        # Open
        self._inner_html.appendleft(_HtmlLine(line=open_tag, indent=Indent.indent))
        # Close
        self.newline(indent=Indent.dedent)
        operator.iadd(self, close_tag)
        self.newline()

    def tag_with_content(
            self,
            content: Union[str, Html],
            *tag_args,
            **tag_attributes
    ) -> None:
        with self.tag(*tag_args, **tag_attributes):
            operator.iadd(self, content)

    def newline(
            self,
            force: bool = False,
            indent: Union[Indent, int] = Indent.nothing
    ) -> None:
        if isinstance(indent, int):
            indent = Indent.from_int(indent)
        if not force and len(self._buffer) == 0 and len(self._inner_html) > 0:
            # No newline
            self._inner_html[-1].indent += indent
            return
        self._inner_html.append(_HtmlLine(line=self._buffer, indent=indent))
        self._buffer = ''

    def to_raw_html(
            self,
            indent_size: int = 2
    ) -> str:
        return_str = ''
        indent = 0
        for html_line in self._inner_html:
            return_str += ' ' * indent_size * indent + html_line.line + '\n'
            indent += html_line.indent.to_int()
            if indent < 0:
                raise WriteOutError('Invalid indentation found.')
        return_str += ' ' * indent_size + self._buffer + '\n'
        return return_str

    def deepcopy(self) -> Html:
        return copy.deepcopy(self)

    def __str__(self) -> str:
        return self.to_raw_html()

    def __add__(self, other: Union[str, Html]) -> Html:
        target = self.deepcopy()
        return operator.iadd(target, other)

    def __iadd__(self, other: Union[str, Html]) -> Html:
        if isinstance(other, str):
            self._buffer += other
            return self
        elif type(other) is Html:
            self.newline()
            for line in other._inner_html:
                self._buffer = line.line
                self.newline(indent=line.indent)
            self._buffer = other._buffer
            return self
        return NotImplemented

    @staticmethod
    def html_template(head: Union[Html, str], body: Union[Html, str]) -> Html:
        return_html = Html('<!DOCTYPE html>')
        with return_html.tag('html'):
            with return_html.tag('head'):
                return_html += head
            with return_html.tag('body'):
                return_html += body
        return return_html

    @staticmethod
    def _get_open_and_close_tags(
            name: str,
            id_: str = None,
            classes: Sequence[str] = None,
            styles: Mapping[str, str] = None,
            attributes: Mapping[str, str] = None,
    ) -> Tuple[str, str]:
        open_tag_content = [name]
        if id_ is not None:
            open_tag_content.append(f'id={ id_ }')
        if classes is not None:
            class_string_joined = ' '.join(classes)
            open_tag_content.append(f'class="{ class_string_joined }"')
        if styles is not None:
            style_strings = []
            for key, val in styles.items():
                style_strings.append(f'{ key }: { val };')
            style_string_joined = ' '.join(style_strings)
            open_tag_content.append(f'style="{ style_string_joined }"')
        if attributes is not None:
            for key, val in attributes.items():
                open_tag_content.append(f'{ key }="{ val }"')
        open_tag = f'<{ " ".join(open_tag_content) }>'
        close_tag = f'</{ name }>'
        return open_tag, close_tag


if __name__ == '__main__':
    import datetime

    head = '<meta charset="utf-8">'
    body = Html()
    with body.tag('div'):
        with body.tag('p') as h:
            h += 'Hello World!'
    with body.tag('dl'):
        body.tag_with_content('Today', name='dt')
        with body.tag('dt') as h:
            h += datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
    print(Html.html_template(head, body).to_raw_html(indent_size=2))

