import re
import json


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
        if len(html) == 1:
            html = html[0]
        return json.dumps(html, indent=4)

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

# print(t13.isHtmlTag())
# print(t14.isHtmlTag())

# print(' * Get HTML Tags')
print('1', t1.getHtmlTags())
print()
print('2', t2.getHtmlTags())
print()
print('3', t3.getHtmlTags())
print()
print('4', t4.getHtmlTags())
print()
print('5', t5.getHtmlTags())
print()
print('6', t6.getHtmlTags())
print()
print('7', t7.getHtmlTags())
print()
print('8', t8.getHtmlTags())
print()
print('9', t9.getHtmlTags())
print()
print('10', t10.getHtmlTags())
print()
print('11', t11.getHtmlTags())
print()
print('12', t12.getHtmlTags())
print()
print('13', t13.getHtmlTags())
print()
print('14', t14.getHtmlTags())
print()
print('15', t15.getHtmlTags())
print()
print('16', t16.getHtmlTags())


# print()
# t1.getHtmlTags()
# print()
# t2.getHtmlTags()
# print()
# t3.getHtmlTags()
# print()
# t4.getHtmlTags()
# print()
# t5.getHtmlTags()
# print()
# t6.getHtmlTags()
# print()
# t7.getHtmlTags()
# print()
# t8.getHtmlTags()
# print()
# t9.getHtmlTags()
# print()
# t10.getHtmlTags()
# print()
# t11.getHtmlTags()
# print()
# t12.getHtmlTags()
# print()
# t13.getHtmlTags()
# print()
# t14.getHtmlTags()
# print()
# t15.getHtmlTags()
# print()
# t16.getHtmlTags()

# print()
# print(' * Extract HTML Tags As Dict')
# print('1', t1.extractHtmlTagAsDict())
# print('2', t2.extractHtmlTagAsDict())
# print('3', t3.extractHtmlTagAsDict())
# print('4', t4.extractHtmlTagAsDict())
# print('5', t5.extractHtmlTagAsDict())
# print('6', t6.extractHtmlTagAsDict())
# print('7', t7.extractHtmlTagAsDict())
# print('8', t8.extractHtmlTagAsDict())
# print('9', t9.extractHtmlTagAsDict())
# print('10', t10.extractHtmlTagAsDict())
# print('11', t11.extractHtmlTagAsDict())
# print('12', t12.extractHtmlTagAsDict())
# print('13', t13.extractHtmlTagAsDict())
# print('14', t14.extractHtmlTagAsDict())
# print('15', t15.extractHtmlTagAsDict())
# print('16', t16.extractHtmlTagAsDict())

# print()
# print(' * Extract Tag Inner HTML')
# # print('1', t1.extractTagInnerHtml())
# # print('2', t2.extractTagInnerHtml())
# # print('3', t3.extractTagInnerHtml())
# # print('4', t4.extractTagInnerHtml())
# print('5', t5.extractTagInnerHtml())
# # print('6', t6.extractTagInnerHtml())
# # print('7', t7.extractTagInnerHtml())
# # print('8', t8.extractTagInnerHtml())
# # print('9', t9.extractTagInnerHtml())
# # print('10', t10.extractTagInnerHtml())
# # print('11', t11.extractTagInnerHtml())
# # print('12', t12.extractTagInnerHtml())
# print('13', t13.extractTagInnerHtml())
# print('14', t14.extractTagInnerHtml())
# print('15', t15.extractTagInnerHtml())
# print('16', t16.extractTagInnerHtml())

# print()
# print(' * Is HTML Tag')
# # print('1', t1.isHtmlTag())
# # print('2', t2.isHtmlTag())
# # print('3', t3.isHtmlTag())
# # print('4', t4.isHtmlTag())
# print('5', t5.isHtmlTag())
# # print('6', t6.isHtmlTag())
# # print('7', t7.isHtmlTag())
# # print('8', t8.isHtmlTag())
# # print('9', t9.isHtmlTag())
# # print('10', t10.isHtmlTag())
# # print('11', t11.isHtmlTag())
# # print('12', t12.isHtmlTag())
# print('13', t13.isHtmlTag())
# print('14', t14.isHtmlTag())
# print('15', t15.isHtmlTag())
# print('16', t16.isHtmlTag())

# print()
# print(' * Is Simple HTML Tag')
# # print('1', t1.isSimpleHtmlTag())
# # print('2', t2.isSimpleHtmlTag())
# # print('3', t3.isSimpleHtmlTag())
# # print('4', t4.isSimpleHtmlTag())
# print('5', t5.isSimpleHtmlTag())
# # print('6', t6.isSimpleHtmlTag())
# # print('7', t7.isSimpleHtmlTag())
# # print('8', t8.isSimpleHtmlTag())
# # print('9', t9.isSimpleHtmlTag())
# # print('10', t10.isSimpleHtmlTag())
# # print('11', t11.isSimpleHtmlTag())
# # print('12', t12.isSimpleHtmlTag())
# print('13', t13.isSimpleHtmlTag())
# print('14', t14.isSimpleHtmlTag())
# print('15', t15.isSimpleHtmlTag())
# print('16', t16.isSimpleHtmlTag())

# print()
# print(' * Does tag contain other tags')
# # print('1', t1.doesTagContainOtherTags())
# # print('2', t2.doesTagContainOtherTags())
# # print('3', t3.doesTagContainOtherTags())
# # print('4', t4.doesTagContainOtherTags())
# print('5', t5.doesTagContainOtherTags())
# # print('6', t6.doesTagContainOtherTags())
# # print('7', t7.doesTagContainOtherTags())
# # print('8', t8.doesTagContainOtherTags())
# # print('9', t9.doesTagContainOtherTags())
# # print('10', t10.doesTagContainOtherTags())
# # print('11', t11.doesTagContainOtherTags())
# # print('12', t12.doesTagContainOtherTags())
# print('13', t13.doesTagContainOtherTags())
# print('14', t14.doesTagContainOtherTags())
# print('15', t15.doesTagContainOtherTags())
# print('16', t16.doesTagContainOtherTags())


# print()
# print(' * Does string contain tags')
# # print('1', t1.doesStringContainTags())
# # print('2', t2.doesStringContainTags())
# # print('3', t3.doesStringContainTags())
# # print('4', t4.doesStringContainTags())
# print('5', t5.doesStringContainTags())
# # print('6', t6.doesStringContainTags())
# # print('7', t7.doesStringContainTags())
# # print('8', t8.doesStringContainTags())
# # print('9', t9.doesStringContainTags())
# # print('10', t10.doesStringContainTags())
# # print('11', t11.doesStringContainTags())
# # print('12', t12.doesStringContainTags())
# print('13', t13.doesStringContainTags())
# print('14', t14.doesStringContainTags())
# print('15', t15.doesStringContainTags())
# print('16', t16.doesStringContainTags())

# print()
# print(' * Does string contain text and tags')
# # print('1', t1.doesStringContainTextAndTags())
# # print('2', t2.doesStringContainTextAndTags())
# # print('3', t3.doesStringContainTextAndTags())
# # print('4', t4.doesStringContainTextAndTags())
# print('5', t5.doesStringContainTextAndTags())
# # print('6', t6.doesStringContainTextAndTags())
# # print('7', t7.doesStringContainTextAndTags())
# # print('8', t8.doesStringContainTextAndTags())
# # print('9', t9.doesStringContainTextAndTags())
# # print('10', t10.doesStringContainTextAndTags())
# # print('11', t11.doesStringContainTextAndTags())
# # print('12', t12.doesStringContainTextAndTags())
# print('13', t13.doesStringContainTextAndTags())
# print('14', t14.doesStringContainTextAndTags())
# print('15', t15.doesStringContainTextAndTags())
# print('16', t16.doesStringContainTextAndTags())


