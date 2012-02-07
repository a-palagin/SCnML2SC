'''
Created on 29.12.2010

@author: Destroyer
'''
from pyparsing import *

def _flatten(L):
    if type(L) is not list: return [L]
    if L == []: return L
    return _flatten(L[0]) + _flatten(L[1:])

def major(expr):
    rep = Forward()
    e2 = expr.copy()
    rep << e2
    def copyTokenToRepeater(s,l,t):
        matchTokens = _flatten(t.asList())
        print matchTokens
        def mustMatchTheseTokens(s,l,t):
            theseTokens = _flatten(t.asList())
            print theseTokens
            if  int(theseTokens[0]) != int(matchTokens[0])+1:
                raise ParseException("",0,"")
        rep.setParseAction( mustMatchTheseTokens, callDuringTry=True )
    expr.addParseAction(copyTokenToRepeater, callDuringTry=True)
    return rep

f = Word( nums ).setParseAction(lambda t:int(t[0]))
ex= f+":"+major(f)

if __name__ == '__main__':
    
    print ex.parseString("3:4")
