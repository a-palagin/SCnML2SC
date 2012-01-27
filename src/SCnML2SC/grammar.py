# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2011 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""

'''
Created on 24.12.2010

@author: Kolb Dmitry
'''
from pyparsing import *

#general tokens
level = Word(nums)
V= Suppress(u"|")
B=u"{{"
E=u"}}"

rusalphas = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
othersym = u"_:.,-*()<>;?!`/+=@\\^~⋖⋗–°—"
symbols=rusalphas + alphanums + othersym
TXT = Word(symbols).setResultsName("TXT")

varB = Literal(u"⋖")
varE = Literal(u"⋗")
varB.setParseAction(replaceWith(u"\\<"))
varE.setParseAction(replaceWith(u"\\>")) 

#function for pyparsing 
#def _flatten(L):
#    if type(L) is not list: 
#        return [L]
#    if L == []: 
#        return L
#    return _flatten(L[0]) + _flatten(L[1:])
#
#def major(expr):
#    rep = Forward()
#    e2 = expr.copy()
#    rep << e2
#    def copyTokenToRepeater(s,l,t):
#        matchTokens = _flatten(t.asList())
#        print matchTokens
#        def mustMatchTheseTokens(s,l,t):
#            theseTokens = _flatten(t.asList())
#            print theseTokens
#            if  int(theseTokens[0]) != int(matchTokens[0])+1:
#                raise ParseException("",0,"")
#        rep.setParseAction( mustMatchTheseTokens, callDuringTry=True )
#    expr.addParseAction(copyTokenToRepeater, callDuringTry=True)
#    return rep



#SCnFieldConcept rule
artCon = u"SCnFieldConcept"+Suppress(V)+ Combine(OneOrMore(TXT^nestedExpr(u"[",u"]")),u" ", adjacent=False)
articleConcept = nestedExpr(B,E,artCon).setResultsName('SCnFieldConcept') 

#link rule
conL = Optional(Suppress(OneOrMore(TXT)) + Suppress(V)) + Combine(OneOrMore(TXT),u" ", adjacent=False)

#conL=delimitedList(OneOrMore(Combine(TXT)),V,True)

link = nestedExpr(u"[[",u"]]",conL).setResultsName('link')

#tagOper
strOps={}
strOps[u"SCn_объединение"] = u"\\cup" 
strOps[u"SCn_пересечение"] = u"\\cap"
strOps[u"SCn_существование"] = u"\\exists"
strOps[u"SCn_строгое_надмножество"] = u"\\supset"
strOps[u"SCn_строгое_подмножество"] = u"\\subset"
strOps[u"SCn_подмножество"] = u"\\subseteq"
strOps[u"SCn_надмножество"] = u"\\supseteq"
strOps[u"SCn_принадлежность"] = u"\\ni"
strOps[u"SCn_принадлежность_элемента"] = u"\\in" 
strOps[u"SCn_непринадлежность"] = u"\\notin"
strOps[u"SCn_не_равно"] = u"\\neq"
strOps[u"SCn_строгое_невключение"] = u"\\not\\subset"
strOps[u"SCn_равно"] = u"="
strOps[u"SCnTextCommentBegin"]=u"<i>/*" 
strOps[u"SCnTextCommentEnd"]=u"*/</i>"
 
def conversionOp(s,l,t):
    global strOps
    t = strOps[t[0]]
    return t
   
cOp = oneOf(strOps.keys()).setParseAction(conversionOp)
tagOper=nestedExpr(B,E,cOp).setResultsName("tagOper")

def conversionMark(s,l,t):
#    print t
#    print t[0][1]
    if t[0][0] == u"SCnTextMain":
        return ["<b>"+t[0][1]+"</b>"]
    
    if t[0][0] == u"SCnTextSecond":
        return ["<i>"+t[0][1]+"</i>"]
    
    if t[0][0] == u"SCnTextKeyword":
        return [t[0][1]]

    if t[0][0] == u"SCnVar":
        return ["\\<"+t[0][1]+"\\>"]


otherTag = nestedExpr(B,E)
breakMark = u"SCnLevel" +V+ level+Optional(V)+ Optional(otherTag^TXT)
breakMark.setParseAction(replaceWith(u"<br/>"))

fontMark = Group(oneOf(u"SCnTextMain SCnTextSecond SCnTextKeyword SCnVar") + Suppress(V) + Combine(OneOrMore(TXT^link),u" ", adjacent=False)).setParseAction(conversionMark)


cMark = fontMark^breakMark
tagMarker = nestedExpr(B,E,cMark).setResultsName("tagMarker") 

#tag rule
tag=tagMarker^tagOper 

#formula
def conversionFormula(s,l,t):
    #print t[0][0]
    return ["<math>"+t[0][0]+"</math>"]  
formula = nestedExpr("<math>","</math>").setResultsName("formula")
formula.setParseAction(conversionFormula) 

unknown = u"{" + Combine(OneOrMore(TXT^link^tag^formula),u" ", adjacent=False) + SkipTo(u"}")+ u"}"

#scnIdtf rule
scnIdtf = Combine(OneOrMore(TXT^link^tag^formula^unknown),u" ", adjacent=False).setResultsName("scnIdtf")

#textIN rule
textIN = Combine(OneOrMore(TXT^link^tag^formula+SkipTo(E)),u" ", adjacent=False).setResultsName('textIN')
textINm = Combine(OneOrMore(TXT^link),u" ", adjacent=False).setResultsName('textINm')

#SCnFieldSpecConSyn rule
conSyn = u"SCnFieldSpecConSyn"+Suppress(V)+level+Suppress(V)+ scnIdtf
SCnFieldSpecConSyn = nestedExpr(B,E,conSyn).setResultsName('SCnFieldSpecConSyn') 

'''
SCnFieldCompComment
SCnFieldSpecConMemberSet
SCnFieldSpecConPropSuperset
SCnFieldSpecConSuperset
SCnFieldSpecConPropSubset
SCnFieldSpecConSemProxim rules
'''
fieldNamesWithTIN = oneOf(u"SCnFieldSpecConPropSubset SCnFieldSpecConSemProxim " \
                          u"SCnFieldSpecConSuperset SCnFieldSpecConMemberSet " \
                          u"SCnFieldCompComment SCnFieldSpecConPropSuperset")

conWithIN = fieldNamesWithTIN+Suppress(V)+level+Suppress(V)+ textIN
SCnFieldWithTIN = nestedExpr(B,E,conWithIN).setResultsName('SCnFieldWithTIN') 

#SCnFieldCompEnum rule
levelEn = level
compEnum= u"SCnFieldCompEnum"+Suppress(V)+level+Suppress(V)+levelEn+Suppress(V)+textIN
SCnFieldCompEnum = nestedExpr(B,E,compEnum).setResultsName('SCnFieldCompEnum')

#SCnFieldSpecConPart rule
conPart= u"SCnFieldSpecConPart"+Suppress(V)+level+Suppress(V)+ Combine(OneOrMore(TXT+SkipTo(E)))
SCnFieldSpecConPart = nestedExpr(B,E,conPart).setResultsName('SCnFieldSpecConPart') 

#SCnFieldSpecConSemEq rule
conSemEq= u"SCnFieldSpecConSemEq"+Suppress(V)+level+Suppress(V)+scnIdtf+Optional(Suppress(V)+Literal(u"cont"))
SCnFieldSpecConSemEq = nestedExpr(B,E,conSemEq).setResultsName('SCnFieldSpecConSemEq') 

#SCnFieldGenRoleElRel rule
genRoleElRel= u"SCnFieldGenRoleElRel"+Suppress(V)+level+Suppress(V)+textINm+Suppress(V)+textIN
SCnFieldGenRoleElRel = nestedExpr(B,E,genRoleElRel).setResultsName('SCnFieldGenRoleElRel') 

#SCnFieldCompArt
compArt= u"SCnFieldCompArt"+Suppress(V)+level+Suppress(V)+oneOf(u'Image Flash Media')+Suppress(V)+scnIdtf
SCnFieldCompArt = nestedExpr(B,E,compArt).setResultsName('SCnFieldCompArt') 

'''
SCnFieldSpecRelDomainSet
SCnFieldSpecRelDomainSuperSet
SCnFieldSpecRelDomainIntersSet
SCnFieldSpecConDef
SCnFieldSpecConUseConst
SCnFieldSpecConStateDef
SCnFieldSpecConStateUnambObjSet
SCnFieldSpecConRuleIdent
SCnFieldSpecConStat
SCnFieldSpecConExample
SCnFieldSpecConSevStat
SCnFieldSpecConExplan
SCnFieldSpecConDomainDef
SCnFieldSpecConDomain 
SCnFieldSpecConRelSchema rules
'''

fieldNamesWithEn = oneOf(u"SCnFieldSpecRelDomainSet SCnFieldSpecRelDomainSuperSet " \
           u"SCnFieldSpecRelDomainIntersSet SCnFieldSpecConDef " \
           u"SCnFieldSpecConUseConst SCnFieldSpecConStateDef " \
           u"SCnFieldSpecConStateUnambObjSet SCnFieldSpecConRuleIdent " \
           u"SCnFieldSpecConStat SCnFieldSpecConExample " \
           u"SCnFieldSpecConSevStat SCnFieldSpecConExplan " \
           u"SCnFieldSpecConDomainDef SCnFieldSpecConDomain " \
           u"SCnFieldSpecConRelSchema SCnFieldSpecRelDomainIntersSet " \
           u"SCnFieldSpecRelDomainIntersSet SCnFieldSpecConPrivDef " \
           u"SCnFieldSpecConGlossLink SCnFieldSpecConАntipode " \
           u"SCnFieldSpecConSCgtext SCnFieldSpecConArt " \
           u"SCnFieldSpecConFormationRule SCnFieldSpecConPrototype " \
           u"SCnFieldSpecConExampleConcepts SCnFieldSpecConExampleConcept")

specCon = fieldNamesWithEn+Suppress(V)+level
SCnFieldWithEnum = nestedExpr(B,E,specCon).setResultsName('SCnFieldWithEnum')

field = Or([
           SCnFieldSpecConSyn,
           SCnFieldWithTIN,
           SCnFieldSpecConPart,
           SCnFieldCompEnum,
           SCnFieldSpecConSemEq,
           SCnFieldGenRoleElRel,
           SCnFieldCompArt,
           SCnFieldWithEnum
           ]).setResultsName("scnField")

body = (articleConcept + ZeroOrMore(field)).setResultsName("body")

scnArticle=Group(Suppress(u"{{SCnBegin}}") + body + Suppress(u"{{SCnEnd}}")).setResultsName('scnArticle')
#scnArticle=nestedExpr(u"{{SCnBegin}}",u"{{SCnEnd}}",body)