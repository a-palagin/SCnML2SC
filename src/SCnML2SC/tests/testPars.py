# -*- coding: utf-8 -*-

'''
Created on 22.09.2010

@author: Dmitry Kolb
'''

import sys
import codecs
import os
import re
import pprint
import logging
print os.pathsep
from SCnML2SC.grammar import scnArticle
from SCnML2SC.grammar import SCnLStatement
from SCnML2SC.grammar import articleConcept
from SCnML2SC import translator

if __name__ == '__main__':

    logging.basicConfig(filename='./test_pars.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filemode='w')
    log = logging.getLogger("SCNML2SC")
    os.environ["http_proxy"] = u"http://kolb:destroyer@192.168.251.11:8080"
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.info('Инициализация приложения')

    path = "./data/part_test.scn"
    pathout = "./data/part_test.scs"
    st = os.stat(path)
    l=st.st_size

    f = codecs.open(path,'r',encoding="utf-8")

    text = f.read(l)
    f.close()
    print(text)

    #print scnArticle.parseString(text)
    tokens = scnArticle.parseString(text)
    #tokens = articleConcept.parseString(text)
    #tokens = SCnLStatement.parseString(text)
    print tokens
    trans = translator.TranslaterForArticle(tokens,log)
    trans.translate(pathout)
