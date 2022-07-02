import re
import json
from pygments import highlight, lexers, formatters
from colorama import Fore
from colorama import Style


class Html:
    def __init__(self, html_string):
        self.html_string = html_string
        self.innerHtml = self.extractTagInnerHtml()
        self.content = self.extractHtmlTagAsDict()

    reHtml = r"(?si)(\<)([a-z][a-z0-9]*\b)(\s*[^>]*)(\>)(.*?)(<\/)\2(\>)"
    reSimpleHtml = r"\<\/?([a-z][a-z0-9]*\b)\s*[^>]*\s*\>"
    reTextAndTags = r"(?i)(.*?)(\<[a-z][a-z0-9]*\s*[^>]*?\/?\>)(.*)(<\/\2\>)?(.*?)"
    reHtmlComment = r"(?si)(\<!--(.*)--\>)"
    reEmptySpacesBetweenTags = r"\>\s*\<"

    def cleanHtml(html_string):
        clean = True
        cleanHtml = ''

        for i in range(0, len(html_string)):
            if html_string[i] in ['<', '"', "'"]:
                clean = False
            if html_string[i] in ['>', '"', "'"] and not clean:
                clean = True
            if not clean:
                cleanHtml += html_string[i]
            else:
                if html_string[i] not in ['\n', '\t', '\r']:
                    cleanHtml += html_string[i]

        return re.sub(Html.reEmptySpacesBetweenTags, '><', cleanHtml).strip()

    def getHtmlTags(self):
        if not self.doesStringContainTextAndTags():
            return False
        html = self.checkForMultipleTags()
        return json.dumps(html, indent=2)

    def printColoredHtmlTags(self):
        if not self.doesStringContainTextAndTags():
            print(False)
        HTML = self.getHtmlTags()
        if type(HTML) != bool: 
            colored_json = highlight(HTML, lexers.JsonLexer(), formatters.TerminalFormatter())
            print(colored_json)
        else:
            print(f"{Fore.GREEN}{self.html_string}{Style.RESET_ALL}")

    def extractTagInnerHtml(self):
        if not self.isHtmlTag():
            return ''
        if self.isHtmlTag():
            match = re.match(Html.reHtml, self.html_string)
            return match[5]
        return ''

    def extractHtmlTagAsDict(self):
        if self.isHtmlTag():
            tag = re.match(Html.reHtml, self.html_string)
            tagName = tag[2]
            cleanTag = Html.cleanHtml(tag[0])
            if self.innerHtml:
                return { 'name': tagName, 'content': cleanTag, 'innerHtml': Html(self.innerHtml).checkForMultipleTags() }
            return { 'name': tagName, 'content':  cleanTag }
        elif self.isSimpleHtmlTag():
            tag = re.match(Html.reSimpleHtml, self.html_string)
            tagName = tag[1]
            cleanTag = Html.cleanHtml((tag[0]))
            return { 'name': tagName, 'content':  cleanTag }
        elif self.isHtmlComment():
            tag = re.match(Html.reHtmlComment, self.html_string)
            return { 'comment':  tag[0] }
        else:
            tag = self.html_string
            return tag

    def isHtmlTag(self):
        self.html_string = Html.cleanHtml(self.html_string)
        match = re.match(Html.reHtml, self.html_string)
        if match:
            if Html.cleanHtml(match[0]) == self.html_string:
                return True
        return False

    def isSimpleHtmlTag(self):
        self.html_string = Html.cleanHtml(self.html_string)
        match = re.match(Html.reSimpleHtml, self.html_string)
        if match:
            if match[0] == self.html_string:
                return True
        return False

    def isHtmlComment(self):
        self.html_string = Html.cleanHtml(self.html_string)
        match = re.match(Html.reHtmlComment, self.html_string)
        if match:
            if match[0] == self.html_string:
                return True
        return False

    def doesTagContainOtherTags(self):
        content = self.extractTagInnerHtml()
        if content:
            if re.match(Html.reHtml, content) or re.match(Html.reSimpleHtml, content):
                return True
        return False

    def doesStringContainTags(self):
        if self.isHtmlTag() or self.isSimpleHtmlTag():
            return True
        else:
            html = re.match(Html.reHtml, self.html_string)
            simpleHtml = re.findall(Html.reSimpleHtml, self.html_string)
            if html or simpleHtml:
                return True
        return False

    def doesStringContainTextAndTags(self):
        textAndHtml = re.match(Html.reTextAndTags, self.html_string)
        if textAndHtml:
            return True
        return False

    def checkForMultipleTags(self):
        if self.isSimpleHtmlTag():
            return self.extractHtmlTagAsDict()
        elif not self.doesStringContainTextAndTags():
            return self.html_string
        tags = []
        if self.isHtmlTag():
            tags.append(self.extractHtmlTagAsDict())
        else:
            while self.html_string:
                self.html_string = self.html_string
                html = re.match(Html.reHtml, self.html_string)
                simpleHtml = re.match(Html.reSimpleHtml, self.html_string)
                textAndTags = re.match(Html.reTextAndTags, self.html_string)
                htmlComment = re.match(Html.reHtmlComment, self.html_string)
                if html and simpleHtml:
                    if simpleHtml.span() < html.span():
                        tag = Html.cleanHtml(html[0])
                        tags.append(Html(tag).extractHtmlTagAsDict())
                        self.html_string = self.html_string.replace(tag, '', 1)
                    elif simpleHtml.span() > html.span():
                        tag = Html.cleanHtml(simpleHtml[0])
                        tags.append(Html(tag).extractHtmlTagAsDict())
                        self.html_string = self.html_string.replace(tag, '', 1)
                elif html:
                    tag = Html.cleanHtml(html[0])
                    tags.append(Html(tag).extractHtmlTagAsDict())
                    self.html_string = self.html_string.replace(tag, '', 1)
                elif simpleHtml:
                    tag = Html.cleanHtml(simpleHtml[0])
                    tags.append(Html(tag).extractHtmlTagAsDict())
                    self.html_string = self.html_string.replace(tag, '', 1)
                elif htmlComment:
                    tag = Html.cleanHtml(htmlComment[0])
                    tags.append(Html(tag).extractHtmlTagAsDict())
                    self.html_string = self.html_string.replace(tag, '', 1)
                elif textAndTags:
                    tag = self.html_string.split('<')[0]
                    if tag:
                        tags.append(Html(tag).extractHtmlTagAsDict())
                    else:
                        tag = self.html_string.split('>')[0]
                        if tag:
                            tags.append(Html(tag).extractHtmlTagAsDict())
                    self.html_string = self.html_string.replace(tag, '', 1)
                else:
                    tags.append(self.html_string)
                    self.html_string = self.html_string.replace(self.html_string, '', 1)
        if len(tags) >= 1:
            return tags
        return tags[0]

test1 = '''<html>
  <body onload='myFunction'>
    <div>
      <h1>*** Hello</h1>
      <p>World! ***</p>
    </div>
    <footer><p></p></footer>
  </body>
</html>'''
test2 = '''<head>
  <title>Test</title>
</head>
<body onload="myFunction">
  <div>
    <h1>*** Hello</h1>
    <p>World! ***</p>
  </div>
  <footer><p></p></footer>
</body>'''
t1 = Html(test1)
t2 = Html(test2)
t3 = Html("<img src='test.gif'>")
t4 = Html('<head><title>Test</title></head>')
t5 = Html('<div><p>Just</p>a<span><br>test</span></div>')
t6 = Html('<span><img src="test.gif"></span>')
t7 = Html('<footer></footer><p></p>')
t8 = Html('<br>')
t9 = Html('Text and tag: <br>')
t10 = Html('Only text')
t11 = Html("<body onload='myFunction'><div><h1>*** Hello</h1><p>World! ***</p></div><footer><p></p></footer></body>")
t12 = Html('<div><h1>*** Hello</h1><p>World! ***</p></div><footer><p></p></footer>')
t13 = Html('<p>Just</p>')
t14 = Html('<br><span><br>test</span>')
t15 = Html('<!-- This     is        a     comment! --><span><br>TEST</span>')
t16 = Html('<span><br>TEST</span><!-- This     is        a     comment! -->')
t17 = Html('<section><span><br>TEST</span><!-- This     is        a     comment! --></section>')

tests = [ t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17 ]

# print(' * Get HTML Tags')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1})", end=' ')
#     print(tests[i].getHtmlTags())
# print()

print(' * Print Colored HTML Tags')
for i in range(0, len(tests)):
    if i > 0:
        print()
    print(f"{i+1})", end=" ")
    tests[i].printColoredHtmlTags()
print()

# print(' * Extract HTML Tags As Dict')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].extractHtmlTagAsDict()}")
# print()

# print(' * Extract Tag Inner HTML')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].extractTagInnerHtml()}")
# print()

# print(' * Is HTML Tag')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].isHtmlTag()}")
# print()

# print(' * Is Simple HTML Tag')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].isSimpleHtmlTag()}")
# print()

# print(' * Does tag contain other tags')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].doesTagContainOtherTags()}")
# print()


# print(' * Does string contain tags')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].doesStringContainTags()}")
# print()

# print(' * Does string contain text and tags')
# for i in range(0, len(tests)):
#     if i > 0:
#         print()
#     print(f"{i+1}) {tests[i].doesStringContainTextAndTags()}")
