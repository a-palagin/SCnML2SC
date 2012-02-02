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
Created on 23.12.2010

@author: Kolb Dmitry
'''
from grammar import scnArticle
import translator
import sys
import os
import traceback
import codecs
import shutil
#from sets import Set


import locale as lc
loc = lc.getlocale()
#lc.setlocale(lc.LC_ALL,'C' )
lc.setlocale(lc.LC_ALL, ('en_US', 'utf8'))
encoding = lc.getlocale()[1]
if not encoding:
    encoding = "utf-8"

reload(sys)

#sys.setdefaultencoding(encoding)
#sys.setdefaultencoding(encoding)
sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")


import wikitools as wt

import ConfigParser 
import logging
from lxml import etree
from lxml import _elementpath
import pyparsing

isKey = False
keynodes = None
SCnkeynodes = None


def _translateArticle(text,oldname,name,log,outputDir):
    #oldname= name
    name = name.replace(':','_')
    name = name.replace('(','_')
    name = name.replace(')','_')
    name = name.replace('.','_')
    name = name.replace(',','_')
    
    pathout = outputDir+"/"+name+".scsy"
    path = outputDir+"/"+name+".scn"

    
    log.info(pathout)
    tokens = None
    try:
        tokens = scnArticle.parseString(text)
        #print tokens
    except pyparsing.ParseException as exs:
        log.error(u'Syntax error in article '+oldname+':')
        log.error(u"Invalid line №: "+str(exs.lineno))
        log.error(u'Line:')
        log.error(str(exs.line))
        log.error(u" "*(exs.column-1) + u"^")

        # reset api scanner to start after this exception location
        #test = "\n"*(pe.lineno-1)+test[pe.loc+1:]
        return ""
#    except pyparsing.ParseFatalException as exf:
#        log.error(u'ParseFatalException error for article '+oldname+':\n'+ str(exf))
#        return
#    except pyparsing.ParseBaseException as ex:
#        log.error(u'ParseBaseException error for article '+oldname+':\n'+ str(ex))
#        return

    if len(tokens)<=0:
        log.error(u'Bad article ' +oldname+ ' => Pyparsing return 0 tokens for article ')
        return ''
    trans = translator.TranslaterForArticle(tokens,log)
    trans.translate(pathout)
    global keynodes
    keynodes |= trans.concepts 
    global isKey, SCnkeynodes
    if not isKey:
        isKey = True
        SCnkeynodes = trans.genKeywords()
        
    log.info(u'Translation was successful!')
    
    return name+".scsy"
    
def _initialize(conf):
#    print os.getcwd() 
#    script_dir = os.path.dirname(os.path.abspath(__file__))
#    print script_dir
    config = ConfigParser.ConfigParser()
    config.read(conf)
    isProxy = config.getboolean('PROXY', 'proxy')
    if isProxy:
        http_proxy = config.get('PROXY', 'http_proxy')
        os.environ["http_proxy"] = http_proxy
    else:
#        print os.environ["http_proxy"]
        os.environ["http_proxy"]=""
    
    LOG_FILENAME = config.get('LOG', 'log_file')
    logging.basicConfig(filename=LOG_FILENAME,
                        level=logging.DEBUG,
                        format=u'%(asctime)s %(name)s %(levelname)s %(message)s',
                        filemode='w')
    log = logging.getLogger("SCNML2SC")
      
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.info(u'Start processing ...')
    input = config.get('TRANS', 'wikiURL')
    category = config.get('TRANS', 'category')
    outputDir = config.get('TRANS', 'output')
    kb_key_segm = config.get('TRANS', 'kb_key_segm')
    scn_key_segm = config.get('TRANS', 'scn_key_segm')

    return log,input,category,outputDir,kb_key_segm,scn_key_segm          

def _genAllkeynodes(segm,set,genNode=False):
    outStr = u""
    if genNode:
        for x in set:
            outStr += u'"'+ x + u'"={};\n'
    for x in set:
        outStr+=u'"' + x + u'" = "'+ segm + u'/'+ x+ u'";\n'
    return outStr

def _genAllkeynodesType(set):
    outStr = u""
    for x in set:

            
        if x[len(x)-1] == u'*':
            outStr += u'stype_relation->"' +  x + u'";\n'

        if x[len(x)-1] == u'_':
            outStr += u'stype_bin_orient_role_rel->"' + x + u'";\n'

    return outStr
     
#def download_new(kb_seg=None, scn_seg=None,outDir=None,conf='wiki2sc.conf',isGenFileCategory=False):
#    global SCnkeynodes, keynodes 
#    keynodes = set()
#    SCnkeynodes = set() 
#    log,input,category,outputDir, kb_key_segm, scn_key_segm = _initialize(conf)
#    
#    if kb_seg:
#        kb_key_segm = kb_seg
#    if scn_seg:
#        scn_key_segm = scn_seg
#    if  outDir:
#        outputDir = outDir   
#    if not os.path.isdir(outputDir):
#        log.error(u'Output directory does not exist')
#        return 
#    site = wt.wiki.Wiki(input+u"/api.php")
#    cat = wt.category.Category(site,u'Категория:'+category)
#    pages = cat.getAllMembers()
#    kbfile = u'#include "keywords.scsy"\n'
#    i=0
#    for page in pages:
#        log.info(u'-'*20 + u'Begin' + u'-'*20)
#        log.info(u'parsing article: ' + page.title)
#        article = page.getWikiText()
#        try:
#            file =_translateArticle(article,page.title,str(i),log,outputDir)
#            if file!="":
#                kbfile+= u'#include "'+file+'"\n'
#        except  Exception as ex:
#            #log.error(u'Handling parse error in article '+x['title']+u':'+ str(ex)+u'\n'+sys.exc_info()[0])
#            log.error(traceback.format_exc())
#        log.info(u'-'*21 + u'End' + u'-'*21)
#        i += 1
#    
#    if isGenFileCategory:
#        f = codecs.open(outputDir+u"/"+category+".scs",'w',encoding="cp1251")
#        f.write(kbfile)
#        f.close()
#    
#    outStr = u'//' + u'='*10 + u'SCn keynodes' + u'='*10 + u'\n' 
#    outStr += _genAllkeynodes(scn_key_segm,SCnkeynodes)
#    outStr += u'\n\n//' + u'='*10 + category+ u' keynodes' + u'='*10 + u'\n' 
#    outStr += _genAllkeynodes(kb_key_segm,keynodes)
#
#    f = codecs.open(outputDir+u"/keywords.scsy",'w',encoding="cp1251")
#    f.write(outStr)
#    f.close()
#    
#    outStr = _genAllkeynodesType(SCnkeynodes)
#    outStr += _genAllkeynodesType(keynodes)
#
#    f = codecs.open(outputDir+u"/keywords_types.scsy",'w',encoding="cp1251")
#    f.write(outStr)
#    f.close()   
     
def downloadFiles(site, outputDirfiles, artName,pageid,log):
    params = {u'action':u'query',u'prop':u'images',u'titles':artName}
    request = wt.api.APIRequest(site, params)
    result = request.query()
    #log.info(result)
    page_cnt = result['query']['pages'][pageid]
    #log.info(page_cnt)
    if u'images' in page_cnt.keys():
        log.info(u'load images for article: ' + artName)
        for x in  page_cnt['images']:
            image_title = x['title']
            log.info(u'load image: ' + image_title) 
            file = wt.wikifile.File(site,image_title)
            loc = image_title.split(':', 1)[1]
            file.download(location = os.path.join(outputDirfiles,loc))
            
def download(kb_seg = None, scn_seg = None, _wikiUrl = None, _category = None, outDir = None, conf = 'wiki2sc.conf', isGenFileCategory = False): 
    global SCnkeynodes, keynodes 
    keynodes = set()
    SCnkeynodes = set() 
    log, input, category, outputDir, kb_key_segm, scn_key_segm = _initialize(conf)
    
    outputDirfiles = u''
    if kb_seg:
        kb_key_segm = kb_seg
    if scn_seg:
        scn_key_segm = scn_seg
    if outDir:
        outputDir = outDir
    if _wikiUrl:
        input = _wikiUrl
    if _category:
        category = _category
    if not os.path.isdir(outputDir):
        log.error(u'Output directory does not exist')
        return 
    outputDirfiles = os.path.join(outputDir,u'files')
    if not os.path.isdir(outputDirfiles):
        os.mkdir(outputDirfiles)
    else:
        shutil.rmtree(outputDirfiles)
        os.mkdir(outputDirfiles)
    site = wt.wiki.Wiki(input + u"/api.php")

    cat = wt.category.Category(site,'Category:'+category)
    pages = cat.getAllMembers()
    #log.info(result)
    kbfile = u'#include "keywords.scsy"\n'
    i=0
    #for x in result[u'query'][u'categorymembers']:
    for page in pages:
        log.info(u'-'*20 + u'Begin' + u'-'*20)
        log.info(u'parsing article:' + page.title )

        params = {u'action':u'query',u'titles':page.title,u'export':u'exportnowrap'}
        
        request = wt.api.APIRequest(site, params)
        result = request.query()
        #log.info(result)

        intext = result['query']['export']['*']
        #print intext
        root = etree.fromstring(intext)
        ns = '{' + root.nsmap[None] + '}' 
        pageid = root.find(ns + 'page/' + ns + 'id').text
        txt = root.find(ns + 'page/' + ns + 'revision/' + ns + 'text')
        
        article = txt.text
        
        try:
            downloadFiles(site, outputDirfiles, page.title,pageid,log)
            file =_translateArticle(article,page.title,str(i),log,outputDir)
            if file!="":
                kbfile+= u'#include "'+file+'"\n'
        except  Exception as ex:
            #log.error(u'Handling parse error in article '+x['title']+u':'+ str(ex)+u'\n'+sys.exc_info()[0])
            log.error(traceback.format_exc())

        log.info(u'-'*21 + u'End' + u'-'*21)
        i += 1
    
    if isGenFileCategory:
        f = codecs.open(outputDir+u"/"+category+".scs",'w',encoding="cp1251")
        f.write(kbfile)
        f.close()
    
    outStr = u'//' + u'='*10 + u'SCn keynodes' + u'='*10 + u'\n' 
    outStr += _genAllkeynodes(scn_key_segm,SCnkeynodes,True)
    
    f = codecs.open(outputDir+u"/keywords_scn.txt",'w',encoding="cp1251")
    f.write(outStr)
    f.close()
    
    outStr = u'//' + u'='*10 + category+ u' keynodes' + u'='*10 + u'\n' 
    outStr += _genAllkeynodes(kb_key_segm,keynodes,True)    
    
    f = codecs.open(outputDir+u"/keywords.scsy",'w',encoding="cp1251")
    f.write(outStr)
    f.close()
    
    outStr = _genAllkeynodesType(SCnkeynodes)
    outStr += _genAllkeynodesType(keynodes)

    f = codecs.open(outputDir+u"/keywords_types.scsy",'w',encoding="cp1251")
    f.write(outStr)
    f.close()

if __name__ == '__main__':
    download(isGenFileCategory=True)
    
        



