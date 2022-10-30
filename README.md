# html-tags-to-json

[*__Test it__*](https://bit.ly/3IgEHoO) ([_Google Colab_](https://colab.research.google.com/))

---

<br><br>

_This script extracts a_ __single HTML tag__ (returns an _object_) _or_ __multiple HTML tags__ (returns a list of objects) _as_ __JSON__.

```json
{
    "name": "head",
    "content": "<head><title>Test</title></head>",
    "innerHtml": {
        "name": "title",
        "content": "<title>Test</title>",
        "innerHtml": "Test"
    }
}
```

---

<br>

## Usage:

<br>

```python
myHtmlContent = Html('<head><title>Test</title></head>')
myHtmlContent.extractHtmlTagAsDict()
```

*__Output__*:

```python
{
    name: 'head',
    content: '<head><title>Test</title></head>',
    innerHtml: {
        name: 'title',
        content: '<title>Test</title>',
        innerHtml: 'Test'
    }
}
```

<br><br>

_If there's no_ `HTML` _content_, _the main extraction function_ (`extractHtmlTagAsDict`) _will just return the_ `string` _back_:

```python
myOnlyTextContent = Html('This is not HTML.')
myOnlyTextContent.extractHtmlTagAsDict()
```

*__Output__*:

```python
'This is not HTML.'
```

<br><br>

_If there's_ `HTML` _content mixed with text and comments_, _the main extraction function_ (`extractHtmlTagAsDict`) _will return an_ `array` _with each tag, text and comment_:

```python
myHtmlAndTextContent = Html('''
    <p>
        This is a paragraph.<br>
    </p>
    This is text with HTML (and a comment).
    <!-- A comment -->
''')
myHtmlAndTextContent.extractHtmlTagAsDict()
```

*__Output__*:

```python
[
    {
        name: 'p':,
        content: '<p>This is a paragraph.<br></p>',
        innerHtml: [
            'This is a paragraph.',
            {
                name: 'br',
                content: '<br>'
            }
        ]
    },
    'This is text with HTML (and a comment).',
    {
        comment: '<!-- A comment -->',
    }
]
```

