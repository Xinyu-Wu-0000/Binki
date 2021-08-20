import os
from sys import stdout
import time
from requests import get
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import hashlib


class BingDict_Word():
    def __init__(self, word: str, media_dir: str) -> None:
        self.word = word
        self.timeout = 5
        self.requset_max_time = 3
        self.requset_err_sleep = 0.1
        self.html_parser = 'html.parser'
        self.media_dir = media_dir
        self.media_prefix = 'BingDictionary'
        self.link_prefix = 'https://www.bing.com'
        self.left_area = Tag(name='div', parser=self.html_parser)
        self.errs_num = 0
        self.errs_logs = []
        self.get_left_area()
        self.phonetic_symbol_US = ''
        self.phonetic_symbol_EN = ''
        self.pronunciation_US = ''
        self.pronunciation_EN = ''
        self.meaning_summary = []
        self.word_transformation = []
        self.word_image = []
        self.collocate = []
        self.synonym = []
        self.antonym = []
        self.Authoritative_English_Chinese_Dual_Explanation = []
        self.Authoritative_English_Chinese_Dual_Explanation_info = {}
        self.sentence = []

    def get_left_area(self):
        for i in range(self.requset_max_time):
            try:
                r = get("https://www.bing.com/dict/search?",
                        params={'q': self.word}, allow_redirects=True, timeout=self.timeout)
                if r.status_code == 200:
                    flag = True
                    break
            except Exception as e:
                flag = False
                err = str(e)
                time.sleep(self.requset_err_sleep)
        if not flag:
            self.errs_num += 1
            self.errs_logs.append('fail to search word '+err)
            return
        self.left_area = BeautifulSoup(
            r.content, self.html_parser, from_encoding='utf-8').find(
                name='div', class_='lf_area')

    def get_phonetic_symbol_US(self):
        self.phonetic_symbol_US = self.left_area.find(
            name='div', class_="hd_prUS b_primtxt")
        if self.phonetic_symbol_US:
            self.phonetic_symbol_US = self.phonetic_symbol_US.string

    def get_phonetic_symbol_EN(self):
        self.phonetic_symbol_EN = self.left_area.find(
            name='div', class_="hd_pr b_primtxt")
        if self.phonetic_symbol_EN:
            self.phonetic_symbol_EN = self.phonetic_symbol_EN.string

    def get_pronunciation_US(self):
        find_via = self.left_area.find(
            name='div', class_="hd_prUS b_primtxt")
        if find_via:
            find_via = find_via.find_next(
                name='div', class_='hd_tf')
            if find_via:
                self.pronunciation_US = find_via.find(
                    name='a', class_='bigaud', onclick=True)
                if self.pronunciation_US:
                    url = re.match(
                        r'^javascript:BilingualDict.Click\(this,\'(.*\.mp3)\'.*$', self.pronunciation_US['onclick'])
                    if url:
                        url = url[1]
                        for i in range(self.requset_max_time):
                            try:
                                aud = get(
                                    url, timeout=self.timeout)
                                if aud.status_code == 200:
                                    flag = True
                                    break
                            except Exception as e:
                                flag = False
                                err = str(e)
                                time.sleep(self.requset_err_sleep)
                        if flag:
                            hash_md5 = hashlib.md5(aud.content).hexdigest()
                            try:
                                open(self.media_dir+self.media_prefix +
                                     hash_md5 + '.mp3', 'wb').write(aud.content)
                                self.pronunciation_US = self.media_prefix+hash_md5+'.mp3'
                            except Exception as e:
                                self.errs_num += 1
                                self.errs_logs.append(
                                    'fail to find pronunciation US '+str(e))
                        else:
                            self.errs_num += 1
                            self.errs_logs.append(
                                'fail to find pronunciation US '+err)
                    else:
                        self.errs_num += 1
                        self.errs_logs.append(
                            'fail to find pronunciation US')
                else:
                    self.errs_num += 1
                    self.errs_logs.append('fail to find pronunciation US')
            else:
                self.errs_num += 1
                self.errs_logs.append('fail to find pronunciation US')
        else:
            self.errs_num += 1
            self.errs_logs.append('fail to find pronunciation US')

    def get_pronunciation_EN(self):
        find_via = self.left_area.find(
            name='div', class_="hd_pr b_primtxt")
        if find_via:
            find_via = find_via.find_next(
                name='div', class_='hd_tf')
            if find_via:
                self.pronunciation_EN = find_via.find(
                    name='a', class_='bigaud', onclick=True)
                if self.pronunciation_EN:
                    url = re.match(
                        r'^javascript:BilingualDict.Click\(this,\'(.*\.mp3)\'.*$', self.pronunciation_EN['onclick'])
                    if url:
                        url = url[1]
                        for i in range(self.requset_max_time):
                            try:
                                aud = get(
                                    url, timeout=self.timeout)
                                if aud.status_code == 200:
                                    flag = True
                                    break
                            except Exception as e:
                                flag = False
                                err = str(e)
                                time.sleep(self.requset_err_sleep)
                        if flag:
                            hash_md5 = hashlib.md5(aud.content).hexdigest()
                            try:
                                open(self.media_dir+self.media_prefix +
                                     hash_md5 + '.mp3', 'wb').write(aud.content)
                                self.pronunciation_EN = self.media_prefix+hash_md5+'.mp3'
                            except Exception as e:
                                self.errs_num += 1
                                self.errs_logs.append(
                                    'fail to find pronunciation EN '+str(e))
                        else:
                            self.errs_num += 1
                            self.errs_logs.append(
                                'fail to find pronunciation EN '+err)
                    else:
                        self.errs_num += 1
                        self.errs_logs.append(
                            'fail to find pronunciation EN')
                else:
                    self.errs_num += 1
                    self.errs_logs.append('fail to find pronunciation EN')
            else:
                self.errs_num += 1
                self.errs_logs.append('fail to find pronunciation EN')
        else:
            self.errs_num += 1
            self.errs_logs.append('fail to find pronunciation EN')

    def get_meaning_summary(self):
        find_via = self.left_area.find(class_='qdef')
        if find_via:
            find_via = find_via.find(name='ul')
            if find_via:
                for single_POS_meaning in find_via.find_all(name='li'):
                    POS = single_POS_meaning.find(class_='pos').string
                    meaning = single_POS_meaning.find(
                        class_='def b_regtxt').string
                    self.meaning_summary.append(
                        {'POS': POS, 'meaning': meaning})
                if len(self.meaning_summary) == 0:
                    self.errs_num += 1
                    self.errs_logs.append('fail to find meaning summary')
            else:
                self.errs_num += 1
                self.errs_logs.append('fail to find meaning summary')
        else:
            self.errs_num += 1
            self.errs_logs.append('fail to find meaning summary')

    def get_word_transformation(self):
        find_via = self.left_area.find(name='div', class_='qdef')
        if find_via:
            find_via = find_via.find(name='div', class_='hd_if')
            if find_via:
                for transform_type_tag in find_via.find_all(name='span', class_='b_primtxt'):
                    transform_type = re.match(
                        r'^(.*?)：', transform_type_tag.string)[1]
                    transformation = transform_type_tag.find_next(
                        name='a', class_='p1-5')
                    try:
                        transformation_link = self.link_prefix + \
                            re.match(r'^(/dict/search\?q=.*?)&.*$',
                                     transformation['href'])[1]
                    except Exception as e:
                        transformation_link = ''
                    transformation = transformation.string
                    self.word_transformation.append(
                        {'transform type': transform_type, 'transformation link': transformation_link, 'transformation': transformation})

    def get_image(self):
        find_via = self.left_area.find(name='div', class_='qdef')
        if find_via:
            find_via = find_via.find(name='div', class_='img_area')
            if find_via:
                for single_image in find_via:
                    url = single_image.a.img['src']
                    for i in range(self.requset_max_time):
                        try:
                            img = get(url, timeout=self.timeout)
                            if img.status_code == 200:
                                flag = True
                                break
                        except Exception as e:
                            flag = False
                            err = str(e)
                            time.sleep(self.requset_err_sleep)
                    if not flag:
                        self.errs_num += 1
                        self.errs_logs.append('fail to get all images '+err)
                        continue
                    hash_md5 = hashlib.md5(img.content).hexdigest()
                    try:
                        open(self.media_dir+self.media_prefix +
                             hash_md5+'.png', 'wb').write(img.content)
                        self.word_image.append(
                            self.media_prefix+hash_md5+'.png')
                    except Exception as e:
                        self.errs_num += 1
                        self.errs_logs.append('fail to get all images '+str(e))

    def get_collocate(self):
        find_via = self.left_area.find(name='div', class_='wd_div')
        if not find_via:
            return
        find_via = find_via.find(name='div', id='colid')
        if not find_via:
            return
        for single_collocate_type_tag in find_via:
            collocate_type = single_collocate_type_tag.find(
                name='div', class_='de_title2 b_dictHighlight').string
            single_collocate = {
                'collocate type': collocate_type, 'collocates': []}
            for collocate in single_collocate_type_tag.find(name='div', class_='col_fl').find_all(name='a'):
                url = self.link_prefix + \
                    re.match(r'^(/dict/search\?q=.*?)&.*$',
                             collocate['href'])[1]
                single_collocate['collocates'].append(
                    {'collocate link': url, 'collcate': collocate.string})
            self.collocate.append(single_collocate)

    def get_synonym(self):
        find_via = self.left_area.find(name='div', class_='wd_div')
        if not find_via:
            return
        find_via = find_via.find(name='div', id='synoid')
        if not find_via:
            return
        for single_synonym_type_tag in find_via:
            synonym_type = single_synonym_type_tag.find(
                name='div', class_='de_title1 b_dictHighlight').string
            single_synonym = {
                'synonym type': synonym_type, 'synonyms': []}
            for synonym in single_synonym_type_tag.find(name='div', class_='col_fl').find_all(name='a'):
                url = self.link_prefix + \
                    re.match(r'^(/dict/search\?q=.*?)&.*$',
                             synonym['href'])[1]
                single_synonym['synonyms'].append(
                    {'synonym link': url, 'synonym': synonym.string})
            self.synonym.append(single_synonym)

    def get_antonym(self):
        find_via = self.left_area.find(name='div', class_='wd_div')
        if not find_via:
            return
        find_via = find_via.find(name='div', id='antoid')
        if not find_via:
            return
        for single_antonym_type_tag in find_via:
            antonym_type = single_antonym_type_tag.find(
                name='div', class_='de_title1 b_dictHighlight').string
            single_antonym = {
                'antonym type': antonym_type, 'antonyms': []}
            for antonym in single_antonym_type_tag.find(name='div', class_='col_fl').find_all(name='a'):
                url = self.link_prefix + \
                    re.match(r'^(/dict/search\?q=.*?)&.*$',
                             antonym['href'])[1]
                single_antonym['antonyms'].append(
                    {'antonym link': url, 'antonym': antonym.string})
            self.antonym.append(single_antonym)

    def get_Authoritative_English_Chinese_Dual_Explanation(self):
        find_via = self.left_area.find(name='div', class_='df_div')
        if not find_via:
            return
        find_via = find_via.find(name='div', id='defid')
        if not find_via:
            return
        find_via = find_via.find(name='div', class_='auth_area', id='authid')
        if not find_via:
            return
        for single_POS in find_via.find_all(name='div', class_='each_seg'):
            try:
                single_POS_type = single_POS.find(
                    name='div', class_='pos').string
            except Exception as e:
                continue
            single_POS_content = {'POS': single_POS_type,
                                  'Explanations': [], 'IDMs': []}
            for tag in single_POS.find(name='div', class_='de_seg'):
                if tag['class'] == ['dis']:
                    Explanation = {'summary CN': '', 'summary EN': ''}
                    Explanation['summary CN'] = tag.find(
                        name='span', class_='bil_dis b_primtxt').string
                    Explanation['summary EN'] = tag.find(
                        name='span', class_='val_dis b_primtxt').string
                    single_POS_content['Explanations'].append(Explanation)

                elif tag['class'] == ['se_lis']:
                    Explanation = {'pattern': '',
                                   'detail CN': '', 'detail EN': '', 'usage': '', 'infor': ''}
                    Explanation['detail CN'] = tag.find(
                        name='span', class_='bil b_primtxt').string
                    Explanation['detail EN'] = tag.find(
                        name='span', class_='val b_regtxt').string
                    pattern = tag.find(
                        name='span', class_='comple b_regtxt')
                    if pattern:
                        Explanation['pattern'] = pattern.string
                    usage = tag.find(name='span', class_='gra b_regtxt')
                    if usage:
                        Explanation['usage'] = usage.string
                    infor = tag.find(name='span', class_='infor b_regtxt')
                    if infor:
                        Explanation['infor'] = infor.string
                    single_POS_content['Explanations'].append(Explanation)
                else:
                    continue
            single_POS_IDM_tag = single_POS.find(
                name='div', class_='idm_seg')
            if single_POS_IDM_tag:
                for tag in single_POS_IDM_tag.find_all(name='div', class_='idm_s'):
                    IDM = {'IDM': '', 'meaning CN': '',
                           'meaning EN': '', 'infor': ''}
                    IDM['IDM'] = tag.span.string
                    IDM['meaning CN'] = tag.next_sibling.find(
                        name='span', class_='bil b_primtxt').string
                    IDM['meaning EN'] = tag.next_sibling.find(
                        name='span', class_='val b_regtxt').string
                    infor = tag.next_sibling.find(
                        name='span', class_='infor')
                    if infor:
                        IDM['infor'] = infor.string
                    single_POS_content['IDMs'].append(IDM)
            self.Authoritative_English_Chinese_Dual_Explanation.append(
                single_POS_content)

        find_via = find_via.find(name='div', class_='synon')
        if not find_via:
            return
        info_type = find_via.find(name='div', class_='sy_la').string
        info = {}

        info['link'] = self.link_prefix + \
            re.match(r'^(/dict/search\?q=.*?)&.*$',
                     find_via.find(name='a', class_='au_ref b_alink')['href'])[1]
        info['content'] = find_via.find(
            name='a', class_='au_ref b_alink').span.string
        self.Authoritative_English_Chinese_Dual_Explanation_info = {
            'info type': info_type, 'info': info}

    def get_sentence(self):
        find_via = self.left_area.find(name='div', id='sentenceSeg')
        if find_via:
            for sentence_tag in find_via.find_all(name='div', class_='se_li'):
                sentence = {'EN': [], 'CN': [],
                            'audio source': {}, 'audio': ''}
                for EN_word_tag in sentence_tag.find(name='div', class_='sen_en b_regtxt'):
                    if EN_word_tag['class'] == ['p1-8', 'b_regtxt'] or EN_word_tag['class'] == ['p1-7', 'b_dictHighlight']:
                        if 'href' in EN_word_tag.attrs:
                            url = self.link_prefix + \
                                re.match(
                                    r'^(/dict/search\?q=.*?)&.*$', EN_word_tag['href'])[1]
                        else:
                            url = ''
                        sentence['EN'].append(
                            {'link': url, 'word': EN_word_tag.string})
                    if EN_word_tag['class'] == ['b_regtxt']:
                        sentence['EN'].append(
                            {'link': '', 'word': EN_word_tag.string})
                for CN_word_tag in sentence_tag.find(name='div', class_='sen_cn b_regtxt'):
                    if CN_word_tag['class'] == ['p1-9', 'b_regtxt'] or CN_word_tag['class'] == ['p1-7', 'b_dictHighlight']:
                        if 'href' in CN_word_tag.attrs:
                            url = self.link_prefix + \
                                re.match(
                                    r'^(/dict/search\?q=.*?)&.*$', CN_word_tag['href'])[1]
                        else:
                            url = ''
                        sentence['CN'].append(
                            {'link': url, 'word': CN_word_tag.string})
                    if CN_word_tag['class'] == ['b_regtxt']:
                        sentence['CN'].append(
                            {'link': '', 'word': CN_word_tag.string})
                find_via = sentence_tag.find(
                    name='div', class_='sen_li b_regtxt')
                if find_via:
                    find_via = find_via.find(
                        name='a', target='_blank', rel='external nofollow', class_='p1-3')
                    if find_via:
                        sentence['audio source'] = {
                            'link': find_via['href'], 'name': find_via.string}
                find_via = sentence_tag.find(name='div', class_='mm_div')
                if find_via:
                    find_via = find_via.find(
                        name='a', class_='bigaud', title='点击朗读')
                    url = re.match(
                        r'^javascript:BilingualDict.Click\(this,\'(https:.*\.mp3)\'.*$', find_via['onmousedown'])[1]
                    for i in range(self.requset_max_time):
                        try:
                            aud = get(url=url, timeout=self.timeout)
                            if aud.status_code == 200:
                                flag = True
                                break
                        except Exception as e:
                            flag = False
                            err = str(e)
                            time.sleep(self.requset_err_sleep)
                    if flag:
                        hash_md5 = hashlib.md5(aud.content).hexdigest()
                        try:
                            open(self.media_dir+self.media_prefix +
                                 hash_md5 + '.mp3', 'wb').write(aud.content)
                            sentence['audio'] = self.media_prefix + \
                                hash_md5+'.mp3'
                        except Exception as e:
                            self.errs_num += 1
                            self.errs_logs.append(
                                'fail to get audio example for all sentence'+str(e))
                    else:
                        self.errs_num += 1
                        self.errs_logs.append(
                            'fail to get audio example for all sentence'+err)
                self.sentence.append(sentence)

    def get_all(self):
        self.get_phonetic_symbol_US()
        self.get_phonetic_symbol_EN()
        self.get_pronunciation_US()
        self.get_pronunciation_EN()
        self.get_meaning_summary()
        self.get_word_transformation()
        self.get_image()
        self.get_collocate()
        self.get_synonym()
        self.get_antonym()
        self.get_Authoritative_English_Chinese_Dual_Explanation()
        self.get_sentence()

    def show_as_text(self, file=stdout):
        print(self.word, file=file)

        print(self.phonetic_symbol_US, file=file)
        print(self.phonetic_symbol_EN, file=file)

        print(self.pronunciation_US, file=file)
        print(self.pronunciation_EN, file=file)

        for i in self.meaning_summary:
            print(i, file=file)

        for i in self.word_transformation:
            print(i, file=file)

        for i in self.word_image:
            print(i, file=file)

        for i in self.collocate:
            print(i, file=file)

        for i in self.synonym:
            print(i, file=file)

        for i in self.antonym:
            print(i, file=file)

        for i in self.Authoritative_English_Chinese_Dual_Explanation:
            print(i['POS'], file=file)
            print(i['Explanations'], file=file)
            print(i['IDMs'], file=file)

        print(self.Authoritative_English_Chinese_Dual_Explanation_info, file=file)

        for i in self.sentence:
            print(i['EN'], file=file)
            print(i['CN'], file=file)
            print(i['audio source'], file=file)
            print(i['audio'], file=file)

        print(self.errs_num, file=file)
        print(self.errs_logs, file=file)
