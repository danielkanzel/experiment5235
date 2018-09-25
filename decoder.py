from html.parser import HTMLParser
pars = HTMLParser()
t = pars.unescape('input3.xml')

print(t)