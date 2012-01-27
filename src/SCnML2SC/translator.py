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
Created on 30.12.2010

@author: Kolb Dmitry
'''
import codecs
import os
import os.path
import base64


object_counter = 0

def gen_id():
   
    global object_counter
    object_counter += 1
    return str(object_counter)  
    
class SCnField:
    def __init__(self,tokens,par,l):
        self.tok = tokens
        self.parentConcept = par
        self.role_attr = {}
        self.level = int(l)
    
    def translate(self):
        return ""
    
    def addToField(self,tokens):
        pass
    
    def searchComponents(self,node,article):
        pass
    
    @staticmethod
    def formatIdtf(txt):
        txt = txt.strip()
        txt = txt.replace("( ","(")
        txt = txt.replace(" )",")")
        txt = txt.replace("{ ","{")
        txt = txt.replace(" }","}")
       
        return txt
    
    def addContype(self,conName):
        #print conName
        return u'stype_sheaf->' + conName + ';\n'  

    
class SCnFieldConcept(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.articleConcept = SCnField.formatIdtf(tokens[1])
    
    def translate(self):
        return u'' 
    #u'"'+self.articleConcept+'"={};\n'

    @staticmethod
    def keywords():
        return set()

            
class SCnFieldSpecConSyn(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainSynonim"]=SCnField.formatIdtf(par)
        self.fields = []
    
    @staticmethod
    def keywords():
        return set([u'основной_',u'синонимы*',u'идентификация*'])
    
    def _isEnd(self,s):
        if s!="Synonim"+str(self.num-1):
            return u","
        else:
            return u"" 
         
    def translate(self):
        conName = "$con" + gen_id()
        elMain  = "$el" +  gen_id()
        output =  elMain + u"={};\n" 
        output += elMain + u'=c=/"' + self.role_attr["MainSynonim"]+ u'"/;\n'
        elems  =  [] 
        for i in range(len(self.role_attr.keys())-1):
            syn = "Synonim" + str(i)
            #output += u'\n  /"'+ self.role_attr[syn] +'"/' + self._isEnd(syn)
            el  = "$el" +  gen_id()
            output +=  el + u"={};\n" 
            output +=  el + u'=c=/"' + self.role_attr[syn] + u'"/;\n'
            elems.append(el)

        output += conName + u'={\n  "oсновной_":' + elMain + u','

        for i in range(len(elems)):
            syn = "Synonim" + str(i)
            output += u'\n  '+ elems[i] + self._isEnd(syn)

        
        output += u"\n};\n"
        conName1 = conName + u'_1'
        
        output += u'"синонимы*"->'+conName+u';\n' + conName1 + u'={\n  1_:'+conName+u',\n  2_:"' + self.role_attr["MainSynonim"]+u'" \n};\n'
        output += u'"идентификация*"->' + conName1 + u';\n'
        output += self.addContype(conName) 
        output += self.addContype(conName1) 

        return output
    
    def addToField(self,tokens):
        txt = tokens.scnIdtf[0] 
        #print txt
        self.role_attr["Synonim"+str(self.num)]=SCnField.formatIdtf(txt)
        self.num += 1
    
    def searchComponents(self,node,article):
        for child in node.parent.childs:
            if child.field[0] ==  self.__class__.__name__:
                if child.field not in self.fields:
                    self.addToField(child.field)
                    self.fields.append(child.field)
                
class SCnFieldSpecConSemEq(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"] = SCnField.formatIdtf(par)
        #self.addToField(tokens)
        self.fields = []
    
    def _isEnd(self,s):
        if s!="Obj"+str(self.num-1):
            return u","
        else:
            return u"" 
    
    @staticmethod
    def keywords():
        return set([u'трансляция*'])
            
    def translate(self):
        conName = "$con" + gen_id()
        output = u''
        elems  = [] 
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj" + str(i)
            el  = "$el" +  gen_id()
            output +=  el + u"={};\n" 
            txt = self.role_attr[syn].replace("\n"," ")
            txt = txt.replace("\r"," ")
            txt = txt.replace("\t"," ")
            output +=  el + u'=c=/"' + txt + u'"/;\n'
            elems.append(el)
            
        output += conName + u'={'
        for i in range(len(elems)):
            syn = "Obj" + str(i)
            output += u'\n  '+ elems[i] + self._isEnd(syn)
        
        output += u"\n};\n\n"
        conName1 = conName + u'_1'
       
        output += conName1 + u'={\n  1_:"'+self.role_attr["MainConcept"]+'",\n  2_:' + conName + u' \n};\n' 
        output += u'"трансляция*"->' + conName1 + u';\n' 
        
        output += self.addContype(conName1)
        output += self.addContype(conName) 

        return output  
    
    def addToField(self,tokens):
        txt = tokens.scnIdtf[0] 
        #print txt
        self.role_attr["Obj"+str(self.num)] = SCnField.formatIdtf(txt)
        self.num += 1
    
    def searchComponents(self,node,article):
        for child in node.parent.childs:
            if child.field[0]==self.__class__.__name__:
                if child.field not in self.fields:
                    self.addToField(child.field)
                    self.fields.append(child.field)   

class SCnFieldCompComment(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=par
        self.addToField(tokens)
    
    @staticmethod
    def keywords():
        return set()

    def translate(self):
        return ""
    
    def addToField(self,tokens):
        pass

    def searchComponents(self,node,article):
        pass

class SCnFieldCompArt(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.addToField(tokens)
    
    @staticmethod
    def keywords():
        return set()

class SCnFieldCompEnum(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.addToField(tokens)
    
    @staticmethod
    def keywords():
        return set()
        
class SCnFieldSpecConPropSubset(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.addToField(tokens)

    @staticmethod
    def keywords():
        return set()
        
    def translate(self):
        conName = "$con" + gen_id()

        output = conName + u'={\n  "надмножество_":"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  "подмножество_":"' + self.role_attr["concept"]+ u'"\n};\n\n'
        output += u'"строгое включение*"->' + conName + ";\n" 
        output += self.addContype(conName) 

        return output
    
    def addToField(self,tokens):
        txt = tokens.textIN[0] 
        #print txt
        self.role_attr["concept"] = SCnField.formatIdtf(txt)
        self.num += 1

class SCnFieldSpecConPropSuperset(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.addToField(tokens)

    @staticmethod
    def keywords():
        return set([u'подмножество_',u"надмножество_",u"строгое включение*"])

    def translate(self):
        conName = "$con" + gen_id()

        output = conName + u'={\n  "подмножество_":"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  "надмножество_":"' + self.role_attr["concept"]+ u'"\n};\n\n'
        output += u'"строгое включение*"->' + conName + ";\n" 
        output += self.addContype(conName) 

        return output
    
    def addToField(self,tokens):
        txt = tokens.textIN[0] 
        #print txt
        self.role_attr["concept"] = SCnField.formatIdtf(txt)
        self.num += 1

class SCnFieldGenRoleElRel(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.addToField(tokens)
        self.obl = SCnField.formatIdtf(tokens[2][0])
        #print tokens[2]
        self.feature = SCnField.formatIdtf(tokens[3][0])
        #print tokens[3]

    @staticmethod
    def keywords():
        return set()

    
    def translate(self):
        output = u'"'+self.obl+'"={ "' +self.feature+u'": "'+ self.role_attr["MainConcept"]+u'" };\n'
        return output
    
class SCnFieldWithEnum(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"] = SCnField.formatIdtf(par)
        self.fields = []

    def addToField(self,tokens):
        txt = tokens.textIN[0] 
        #print txt
        self.role_attr["Obj"+str(self.num)] = SCnField.formatIdtf(txt)
        self.num += 1
    
    def searchComponents(self,node,article):
        for child in node.childs:
            if child.field[0] == u"SCnFieldCompEnum":
                if child.field not in self.fields:
                    self.addToField(child.field)
                    self.fields.append(child.field)
    @staticmethod
    def keywords():
        return set()
    
class SCnFieldSpecRelDomainSet(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'отношения, области определения которых являются надмножеством описываемого множества и каждая связка которых связывает элементы описываемого множества между собой*'])


    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"'+ self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  2_:' + setName+ u'\n};\n\n'
        output += u'"отношения, области определения которых являются надмножеством описываемого множества и каждая связка которых связывает элементы описываемого множества между собой*"->'+conName+";\n"
        output += self.addContype(conName) 
        output += self.addContype(setName) 
         
        return output
    
class SCnFieldSpecRelDomainSuperSet(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'отношения, области определения которых являются надмножеством описываемого множества и связки которых, в общем случае, связывают элементы описываемого множества с другими объектами*'])


    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"'+ self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  2_:' + setName+ u'\n};\n\n'
        output += u'"отношения, области определения которых являются надмножеством описываемого множества и связки которых, в общем случае, связывают элементы описываемого множества с другими объектами*"->'+conName+";\n" 
        output += self.addContype(conName) 
        output += self.addContype(setName) 

        return output

class SCnFieldSpecRelDomainIntersSet(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'отношения, области определения которых строго пересекаются с описываемым множеством*'])


    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"'+ self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  2_:' + setName+ u'\n};\n\n'
        output += u'"отношения, области определения которых строго пересекаются с описываемым множеством*"->'+conName+";\n" 
        output += self.addContype(conName) 
        output += self.addContype(setName) 

        return output

class SCnFieldSpecConRelSchema(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'схема отношения*'])
    
    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"'+ self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
        output += u'  2_:' + setName+ u'\n};\n\n'
        output += u'"схема отношения*"->' + conName + ";\n" 
        output += self.addContype(conName) 
        output += self.addContype(setName) 
        
        return output

class SCnFieldSpecConDomainDef(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'область определения*'])

    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj" + str(i)
            conName = "$con" + gen_id() + '_' + str(i)
            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
            output += u'  2_:"' + self.role_attr[syn]+ u'"\n};\n\n'
            output += u'"область определения*"->' + conName + u';\n'
            output += self.addContype(conName) 
            
        return output

class SCnFieldSpecConDomain(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'домен*'])

    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            conName = "$con" + gen_id() + '_' + str(i)

            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
            output += u'  2_:"' + self.role_attr[syn]+ u'"\n};\n\n'
            output += u'"домен*"->' + conName + u';\n'
            output += self.addContype(conName) 

        return output


class SCnFieldSpecConDef(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'определение*'])


    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            conName = "$con" + gen_id() + '_' + str(i)

            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
            output += u'  2_:"' + self.role_attr[syn]+ u'"\n};\n\n'
            output += u'"определение*"->' + conName + u';\n'
            output += self.addContype(conName) 
        
        return output

class SCnFieldSpecConExplan(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'пояснение*'])

    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"' + self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:' + setName  + u',\n' 
        output += u'  2_:"'+ self.role_attr["MainConcept"] + u'"\n};\n\n'
        output += u'"пояснение*"->' + conName + ";\n"
        output += self.addContype(conName) 
        output += self.addContype(setName)
        return output
    

class SCnFieldSpecConUseConst(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'используемые константы*'])

    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"'+ self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"] + u'",\n'
        output += u'  2_:' + setName+ u'\n};\n\n'
        output += u'"используемые константы*"->' + conName + ";\n"
        output += self.addContype(conName) 
        output += self.addContype(setName)  
        return output
    
class SCnFieldSpecConStateDef(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'утверждение определяющего типа*'])

    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            conName = "$con" + gen_id() + '_' + str(i)

            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
            output += u'  2_:"' + self.role_attr[syn]+ u'"\n};\n\n'
            output += u'"утверждение определяющего типа*"->' + conName + u';\n'
            output += self.addContype(conName)             

        return output
    
class SCnFieldSpecConStateUnambObjSet(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'утверждение об однозначном задании*'])

    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            conName = "$con" + gen_id() + '_' + str(i)

            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"]+ u'",\n'
            output += u'  2_:"' + self.role_attr[syn]+ u'"\n};\n\n'
            output += u'"утверждение об однозначном задании*"->' + conName + u';\n'
            output += self.addContype(conName) 
        return output

#class SCnFieldSpecConStat(SCnFieldWithEnum):
#    def __init__(self,tokens,par,l):
#        SCnFieldWithEnum.__init__(self,tokens,par,l)
#
#    def translate(self):
#        return ""
#
#    @staticmethod
#    def keywords():
#        return set()
#
#class SCnFieldSpecConRuleIdent(SCnFieldWithEnum):
#    def __init__(self,tokens,par,l):
#        SCnFieldWithEnum.__init__(self,tokens,par,l)
#
#    def translate(self):
#        return ""
#    
#    @staticmethod
#    def keywords():
#        return set()

class SCnFieldSpecConMemberSet(SCnField):
    def __init__(self,tokens,par,l):
        SCnField.__init__(self,tokens,par,l)
        self.num = 0
        self.role_attr["MainConcept"]=SCnField.formatIdtf(par)
        self.el = SCnField.formatIdtf(tokens[2][0])

    @staticmethod
    def keywords():
        return set()

    
    def translate(self):
        output = u'"'+self.el+'"->"'+ self.role_attr["MainConcept"]+u'";\n'
        return output
    
class SCnFieldSpecConExample(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'пример_'])

    def translate(self):
        output = ""
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += u'"' + self.role_attr["MainConcept"] + u'"={ "пример_": "'+ self.role_attr[syn] + u'" };\n\n'
        return output

class SCnFieldSpecConSevStat(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)

    @staticmethod
    def keywords():
        return set([u'утверждение*'])

    def translate(self):
        conName = "$con" + gen_id()
        setName = "$set" + gen_id()
        output = setName +  "={};\n"
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += setName+ u'->"' + self.role_attr[syn] +'";\n'
        output += conName + u'={\n  1_:' + setName  + u',\n' 
        output += u'  2_:"'+ self.role_attr["MainConcept"] + u'"\n};\n\n'
        output += u'"утверждение*"->' + conName + ";\n"
        output += self.addContype(conName) 
        output += self.addContype(setName)  
        return output

#    def translate(self):
#        output = ""
#        for i in range(len(self.role_attr.keys())-1):
#            syn = "Obj" + str(i)
#            conName = "$con" + gen_id() + '_' + str(i)
#
#            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"] + u'",\n'
#            output += u'  2_:"' + self.role_attr[syn] + u'"\n};\n\n'
#            output += u'"утверждение*"->' + conName + u';\n'
#            output += self.addContype(conName)             
#        return output
                    
class SCnFieldSpecConPart(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)
        self.feature = tokens[2]
        #print tokens[2]
    
    def _isEnd(self,s):
        if s!="Obj"+str(self.num-1):
            return u","
        else:
            return u"" 

    @staticmethod
    def keywords():
        return set([u'разбиение*'])
    
    def translate(self):
        conName = "$con"+gen_id()
        output = conName+"={};\n\n"
        output += self.addContype(conName)  
        conName1 = conName + u'_1'
        output += conName1 + u'={\n  1_:'+conName+u',\n  2_:"' + self.role_attr["MainConcept"]+u'" \n};\n\n'
        output += u'"разбиение*"->' + conName1 + u';\n'
        output += self.addContype(conName1)  
        for i in range(len(self.role_attr.keys())-1):
            syn = "Obj"+str(i)
            output += conName+ u'->"'+ self.role_attr[syn] +'";\n'

        return output
    
class SCnFieldSpecConArt(SCnFieldWithEnum):
    def __init__(self,tokens,par,l):
        SCnFieldWithEnum.__init__(self,tokens,par,l)
        self.types = {}
        self.types [u'.jpg'] = u'ui_format_jpg' 
        self.types [u'.jpeg'] = u'ui_format_jpeg' 
        self.types [u'.png'] = u'ui_format_png' 
        self.types [u'.bmp'] = u'ui_format_bmp'
        self.types [u'.avi'] = u'ui_format_avi'
        self.types [u'.flv'] = u'ui_format_flv'
        self.types [u'.mp4'] = u'ui_format_mp4' 
        self.types [u'.mpg'] = u'ui_format_mpg' 
        self.types [u'.wmv'] = u'ui_format_wmv' 
        #self.types [u'.gwf'] = u'ui_format_gwf'
        self.article  = None
        #self.type = tokens[2]
        #print tokens[2]
    
    def _isEnd(self,s):
        if s!="Obj"+str(self.num-1):
            return u","
        else:
            return u"" 

    @staticmethod
    def keywords():
        return set([u'иллюстрация*'])
    
    def getCont(self,path):
        path  = os.path.abspath(path) 
        f = codecs.open(path,'rb')
        st = os.stat(path)
        l = st.st_size
        data = f.read(l)
        f.close()
        return base64.b64encode(data)

    def printPipe(self,out, pipe,log):
        import string
        for line in pipe.readlines():
            self.article.log.error(string.strip(line))
        out.flush()
        
    def downloadYoutube(self,id):
        from subprocess import Popen, PIPE ,call
        import sys
        self.article.log.info(u"Starting youtube-dl for " + u'http://www.youtube.com/watch?v='+id)

        fname = u'file' + gen_id() + u'.flv'

        path  =  os.path.join(self.article.filePath, fname)
        #cmd = u"youtube-dl.exe -o " +path +' '+ u'http://www.youtube.com/watch?v='+id
        
        #st = call([u'youtube-dl.exe', u'-o', path,u'http://www.youtube.com/watch?v='+id])
        if not os.path.exists(u'./youtube-dl.exe'):
            self.article.log.warning(u" youtube-dl.exe does not found ")
            return None 
        cmd = '%s -o "%s" "%s"' % (u'youtube-dl.exe', path, 'http://www.youtube.com/watch?v='+id)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        proc.wait()
        proc.stdout.close()
        
        try:
            if proc.returncode == 0:
                self.article.log.info(u"Loaded " + path)
                
            else:
                #print >> sys.stderr, "In file %s:" % (pathSrc)
                self.printPipe(sys.stderr, proc.stderr, self.article.log)
                return id
        finally:
            proc.stderr.close()
        
        return fname 
    
    def translate(self):
        output = ""
        for i in range((len(self.role_attr.keys())-1)/2):
            syn = "Obj" + str(i)
            type ="Type" +  str(i)
            conName = "$con" + gen_id() + '_' + str(i)
            elName = "$el" + gen_id() + '_' + str(i)
            output += elName + u'={};\n'
            #print self.role_attr[type]
            if self.role_attr[type] == u'Media':
                fname =  self.downloadYoutube(self.role_attr[syn])
                if not fname:
                    self.article.log.warning(u"Error Youtube downloading for id: " + self.role_attr[syn])
                    continue
                self.role_attr[syn] = fname
                
            path  =  os.path.join(self.article.filePath, self.role_attr[syn])
            if not os.path.exists(path):
                self.article.log.warning(u"file " + path + u" does not exist")
                continue 

            cont  = self.getCont(path)
            output += elName + u'=b64/"' + cont + u'"/;\n'
            for end in self.types.keys():
                if self.role_attr[syn].endswith(end):
                    output += self.types[end] + u'->' + elName + u';\n'
                    break 
            output += conName + u'={\n  1_:"' + self.role_attr["MainConcept"] + u'",\n'
            output += u'  2_:"' + elName + u'"\n};\n\n'
            output += u'"иллюстрация*"->' + conName + u';\n'
            output += self.addContype(conName)             
        return output
    
    def addToField(self,tokens):
        txt = tokens.scnIdtf[0] 
        #print txt
        self.role_attr["Obj"+str(self.num)] = SCnField.formatIdtf(txt)
        self.role_attr["Type"+str(self.num)] = SCnField.formatIdtf(tokens[2])

        self.num += 1
    
    def searchComponents(self,node,article):
        self.article = article 
        for child in node.childs:
            if child.field[0] == u"SCnFieldCompArt":
                if child.field not in self.fields:
                    self.addToField(child.field)
                    self.fields.append(child.field)                    

class Node:
    def __init__(self,root,parent):
        self.field = root
        self.childs = []
        self.parent = parent
    
    def dump(self,log):
        log.debug(u"============")
        log.debug(u"Root:") 
        log.debug(self.field)
        log.debug(u"Childs:") 
        for x in self.childs:
            log.debug(x.field)
        log.debug(u"============")
      
          
             
class TranslaterForArticle:

    def __init__(self,toks,log):
        self.relationList = {}
        self.fieldFact={}
        self.articleConcept = u""
        self.currConcept = None
        self.lConcepts = []
        self.curLevel = 0
        self.prevLevel = 0
        self.fieldList=[]
        self.countField=0
        self.tokens=None
        self.processDict=[]
        self.lst = None
        self.Root = None
        self.log = log
        self.tokens = toks
        self.concepts = set()
        self.fieldFact[u"SCnFieldConcept"] = SCnFieldConcept 
        self.fieldFact[u"SCnFieldSpecConSyn"] = SCnFieldSpecConSyn
        self.fieldFact[u"SCnFieldCompComment"] = SCnFieldCompComment
        self.fieldFact[u"SCnFieldCompEnum"] = SCnFieldCompEnum
        self.fieldFact[u"SCnFieldSpecConPropSuperset"] = SCnFieldSpecConPropSuperset
        self.fieldFact[u"SCnFieldSpecConPart"] = SCnFieldSpecConPart
        self.fieldFact[u"SCnFieldSpecRelDomainSet"] = SCnFieldSpecRelDomainSet
        self.fieldFact[u"SCnFieldSpecRelDomainSuperSet"] = SCnFieldSpecRelDomainSuperSet
        self.fieldFact[u"SCnFieldSpecRelDomainIntersSet"] = SCnFieldSpecRelDomainIntersSet
        self.fieldFact[u"SCnFieldSpecConDef"] = SCnFieldSpecConDef
        self.fieldFact[u"SCnFieldSpecConUseConst"] = SCnFieldSpecConUseConst
        self.fieldFact[u"SCnFieldSpecConSemEq"] = SCnFieldSpecConSemEq
        self.fieldFact[u"SCnFieldGenRoleElRel"] = SCnFieldGenRoleElRel
        self.fieldFact[u"SCnFieldSpecConStateDef"] = SCnFieldSpecConStateDef
        self.fieldFact[u"SCnFieldSpecConStateUnambObjSet"] = SCnFieldSpecConStateUnambObjSet
        #self.fieldFact[u"SCnFieldSpecConRuleIdent"] = SCnFieldSpecConRuleIdent
        #self.fieldFact[u"SCnFieldSpecConStat"] = SCnFieldSpecConStat
        self.fieldFact[u"SCnFieldSpecConExample"] = SCnFieldSpecConExample
        self.fieldFact[u"SCnFieldSpecConSevStat"] = SCnFieldSpecConSevStat
        self.fieldFact[u"SCnFieldSpecConDomainDef"] = SCnFieldSpecConDomainDef
        self.fieldFact[u"SCnFieldSpecConDomain"] = SCnFieldSpecConDomain
        self.fieldFact[u"SCnFieldSpecConExplan"] = SCnFieldSpecConExplan
        self.fieldFact[u"SCnFieldSpecConMemberSet"] = SCnFieldSpecConMemberSet
        self.fieldFact[u"SCnFieldSpecConRelSchema"] = SCnFieldSpecConRelSchema
        self.fieldFact[u"SCnFieldSpecConPropSubset"] = SCnFieldSpecConPropSubset
        self.fieldFact[u"SCnFieldCompArt"] = SCnFieldCompArt 
        self.fieldFact[u"SCnFieldSpecConArt"] = SCnFieldSpecConArt   

    def translate(self,outpath):
        self.__analysisDict()
        self.filePath = os.path.join(os.path.dirname(outpath),u'files')

        ostr = self.__generate()
        f = codecs.open(outpath,'w',encoding="cp1251")
        f.write(ostr)
        f.close()
    
    def genKeywords(self):
        output = set()
        for x in self.fieldFact.keys():
            output |= self.fieldFact[x].keywords()

#        f = codecs.open(outpath,'w',encoding="cp1251")
#        f.write(output)
#        f.close()
        return output
     
    def __generate(self):
        ostr=u""
        
        for x in self.lConcepts:
            #print x
            for y in self.relationList[x].keys():
                #print y
                for f in self.relationList[x][y]:
                    ostr += f.translate() 

        return ostr
                
    def __analysisDict(self):
        self.countField = 0
        self.curLevel = 0
        for tok in self.tokens:
            for body in tok:
                #for field in body:
                self.processDict.append([body,False])
        
        self.__genTree(self.processDict)
        
        #self.processing(self.curLevel,None,self.currConcept,0)
        conc = self.getConcept(self.processDict[0][0])
        self.relationList[conc] = {}
               
        self.treeProcessing(self.Root)
        self.__genObjField(self.processDict[0][0],conc,0) 
                     
    def __genTree(self,fields):
        self.Root = Node(fields[0][0],None)
        self.genChilds(self.Root,0,fields,1)

        
    def genChilds(self,root,level,fields,count):
        l = len(fields)    
        #print level
        #print count
        for i in range(count,l):
            if fields[i][1]: 
                continue
            #print fields[i][0]
            if level+1 == int(fields[i][0][1]):
                fields[i][1] = True
                child = Node(fields[i][0],root)
                root.childs.append(child)
                if i+1 < l:
                    if fields[i+1][0][0]!=u"SCnFieldCompComment":
                        if int(fields[i+1][0][1]) == level+2:
                            self.genChilds(child,level+1,fields,i+1)
                    elif fields[i+1][0][0]==u"SCnFieldCompComment":
                        if i+2 < l:
                            if int(fields[i+2][0][1]) == level+2:
                                self.genChilds(child,level+1,fields,i+2)
            elif int(fields[i][0][1]) <= level:
                return           
                        
        
    def treeProcessing(self,root):
        if not root:
            self.log.error(u"treeProcessing treeRoot is None")
            #return
        conc = self.getConcept(root.field)
        currConcept = None
        if conc:
            self.currConcept = conc
            currConcept = conc
            self.relationList[conc] = {}
            self.lConcepts.append(conc)
       
        if not currConcept:
            currConcept = self.currConcept 
        #self.log.debug(currConcept)
        #root.dump(self.log)
        level = 0
        if root.field[0] != u"SCnFieldConcept":
            level = int(root.field[1])

           
        for node in root.childs:
            #self.log.debug(node.field)
            objField = self.__genObjField(node.field,currConcept,level)
            
            if not objField: continue
           
            objField.searchComponents(node,self)
            if len(node.childs)>0:
                self.treeProcessing(node)
           
    def __genObjField(self,field,currConcept,level):
        #print field
        if self.__isSingletonForConcept(field):
            return self.__genObjSingletonField(field,currConcept,level)
        else:
            return self.__genObjMultiField(field,currConcept,level)
        
    def __genObjMultiField(self,field,currConcept,level):
        '''
         Генерируем объект поля для тех полей, которым может соотвествовать много связок 
         для данного концепта 
        '''
        objField = None
        if self.fieldFact.has_key(field[0]):
            objField = self.fieldFact[field[0]](field,currConcept,level)
            if not self.relationList[currConcept].has_key(field[0]):
                self.relationList[currConcept][field[0]] = []
            self.relationList[currConcept][field[0]].append(objField)
            self.fieldList.append(objField)
        else:
            self.log.warning(u"Field " + field[0] + " has no implimentation")

        return objField
    
    def __genObjSingletonField(self,field,currConcept,level):
        '''
         Генерируем объект поля для тех полей, которым может соотвествовать одна связка 
         для данного концепта 
        '''
        objField = None
        if not self.relationList[currConcept].has_key(field[0]):
            objField = self.__genObjMultiField(field,currConcept,level)
        else:
            objField = self.relationList[currConcept][field[0]][0]
        
        return objField
        
    
    def __isSingletonForConcept(self,field):
        '''
        Метод проверят текущую строку разбора
        на предмет создания по ней новой связки отношения 
        ''' 
        singletonsField = [u"SCnFieldSpecConSyn",u"SCnFieldSpecConSemEq"]
        return field[0] in singletonsField
    
    def addToKeynodeSet(self,keynode):
        keynode = SCnField.formatIdtf(keynode)
        if keynode not in self.concepts:  
            self.concepts.add(keynode)
            
    def getConcept(self,tok):
        
        if tok[0] == u"SCnFieldConcept":
            self.addToKeynodeSet(tok[1])
            return tok[1]
        
        conceptField = [u"SCnFieldCompEnum",u"SCnFieldSpecConSyn",u"SCnFieldSpecConPropSuperset"]
        if tok[0] in conceptField :
            if tok[0] == u"SCnFieldCompEnum":
                self.addToKeynodeSet(tok.textIN[0])
                return tok.textIN[0]
            
            txt = tok.scnIdtf[0]
            self.addToKeynodeSet(txt) 
            return txt
            
        else : 
            return None      
       
        