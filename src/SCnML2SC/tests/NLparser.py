# -*- coding: utf-8 -*-
'''
Created on 22.09.2010

@author: Dmitry Kolb
'''


from pyparsing import *



level = Word(nums)

#alphas = u''.join(unichr(x) for x in xrange(0x000, 0xfff) if unichr(x) != u"\n" or unichr(x) != u"\r" )
alphas = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
scnText = Forward()

#txt = Word(alphas)-~keyword-~comment
RESERVED_LITERALS = [u'{{SCnTextCommentBegin}}',
                     u'{{SCnTextCommentEnd}}',
                     u"{{SCnTextMain", 
                     u"{{SCnTextSecond", 
                     u"{{SCnTextKeyword",
                     u"}}",
                     u"\r\n",
                     u"{{SCnLevel"
                     ]
reservedLiteral = MatchFirst(map(Literal, RESERVED_LITERALS))
txt = ~reservedLiteral+Word(alphas+printables+" \t")
txt.setWhitespaceChars(" \t")
print alphas+printables
#DWC = "".join(x for x in txt.DEFAULT_WHITE_CHARS if x != "\n" or x != "\r")
#txt.setDefaultWhitespaceChars(DWC)
txt.setName('txt').setDebug()

name = Combine(ZeroOrMore(txt), adjacent=False)
lnConcept = Combine(ZeroOrMore(txt), adjacent=False)

linkContent = Optional(name + Suppress("|")) + lnConcept
link  = nestedExpr("[[","]]",linkContent)
# SCn-комментарий
#incomment = Combine(ZeroOrMore(CharsNotIn(u"{{SCnTextCommentEnd}}").setName('incomment').setDebug()))
comment = QuotedString(quoteChar=u"{{SCnTextCommentBegin}}",endQuoteChar=u"{{SCnTextCommentEnd}}").setName('comment').setDebug()

marker = oneOf(u"{{SCn_синонимия}} {{SCn_не_равно}} {{SCn_строгое_надмножество}} {{SCn_строгое_подмножество}} \
{{SCn_надмножество}} {{SCn_подмножество}} {{SCn_принадлежность}} \
{{SCn_принадлежность_элемента}} {{SCn_семантическая_эквивалентность}} {{SCn_семантическая_близость}} \
{{SCn_тире}} {{SCn_перечисление}}")

param  = Group(level ^ level + Suppress(u"|") + marker.setResultsName('scnmarker')).setName('param').setDebug()

# Terminal символ уровня
levelField = Suppress(u"{{")+Suppress(u"SCnLevel") +Suppress(u"|")+ param + SkipTo(u"}}",include=True)

keywordName = oneOf(u"SCnTextMain SCnTextSecond SCnTextKeyword")

quotedKeyword = u'''
SCnTextCommentBegin
SCnTextCommentEnd
SCnFrameBegin
SCnFrameEnd
'''.split()

concept = CharsNotIn(u"}}" )

keyword = Group(Suppress(u"{{")+keywordName.setResultsName('keywordName')+Suppress(u"|") + 
                concept.setResultsName('concept')+u"}}").setName('keyword').setDebug()
#Group(QuotedString("{{",escChar="\\",endQuoteChar="}}").setParseAction(do_keyword)).setResultsName('keyword')

fieldEnd=OneOrMore(Literal(u"\r\n")).setName('filedEnd').setDebug()


#txt.ignore(keyword)

scnText << Optional(keyword^comment)+ Combine(ZeroOrMore(txt), adjacent=False)

#DWC = "".join(x for x in scnText.DEFAULT_WHITE_CHARS if x != "\n")
#scnText.setDefaultWhitespaceChars(DWC)
scnText.setName('scnText').setDebug()

#fieldContent=Group(scnText).setName("fieldContent").setDebug()

field = Group(levelField+scnText).setName('field').setDebug()


fields = OneOrMore(field)
fields.setWhitespaceChars("\r\n")

article = Group(Suppress(u"{{SCnBegin}}") + fields | u"{{SCnEnd}}").setName('article').setDebug()