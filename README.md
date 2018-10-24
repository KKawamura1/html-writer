html-writer
---

Simple html writer class for python


## Description

You can write raw html with 'with' statements like:
```python
html = Html()
with html.tag('div'):
    with html.tag('p') as h:
        h += 'Hello world!'
# Here html has '<div><p>Hello world!</p></div>'
``` 

'with' syntax also serves human-readable indentation:
```python
html = Html()
with html.tag('div'):
    with html.tag('p') as h:
        h += 'Hello world!'
# Here html really has 
# <div>
#   <p>
#     Hello world!
#   </p>
# </div>
``` 

## Installation
```bash
pip install html_writer
```


## Example
```python
from html_writer import Html
import datetime

head = Html()
head.self_close_tag('meta', attributes=dict(charset='utf-8'))
body = Html()
with body.tag('div'):
    with body.tag('p') as h:
        h += 'Hello World!'
with body.tag('dl'):
    body.tag_with_content('Today', name='dt')
    with body.tag('dt') as h:
        h += datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
print(Html.html_template(head, body).to_raw_html(indent_size=2))
```

## Requirements
- Python >= 3.7.0

## Frequently Asked Questions

Q. Isn't it reinventing the wheel? :) :) :)

A. Enjoy coding!
