# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

import os
import re
import threading
import json
import urllib.request

from .bingdict_word import BingDict_Word


def create_and_show_add_word_window() -> None:
    win = add_word_window(parent=mw)
    win.show()


class add_word_window(QMainWindow):
    done_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.word = ''
        self.lock = threading.Lock()
        self.done_signal.connect(self.update_html)
        self.path = os.path.abspath(__file__)
        self.file = os.path.basename(__file__)
        self.path = re.match(rf'^(.*){self.file}$', self.path)[1]
        with open(self.path+'config.json', 'r') as f:
            self.config = json.load(f)
        self.back_ground_color = self.palette().color(QPalette.Base).name()
        self.text_color = self.palette().color(QPalette.Text).name()
        self.deckNames = ''

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('welcome to Binki')

        self.main_frame = QWidget(self)
        self.vboxlayout = QVBoxLayout(self)
        self.main_frame.setLayout(self.vboxlayout)
        self.setCentralWidget(self.main_frame)

        self.hboxlayout1 = QHBoxLayout(self)
        self.label1 = QLabel(self)
        self.label1.setText('word to add: ')
        self.hboxlayout1.addWidget(self.label1)
        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.returnPressed.connect(self.on_click_search)
        self.hboxlayout1.addWidget(self.lineEdit1)
        self.enter_botton = QPushButton(self)
        self.enter_botton.setText('Search')
        self.enter_botton.clicked.connect(self.on_click_search)
        self.hboxlayout1.addWidget(self.enter_botton)
        self.label2 = QLabel(self)
        self.label2.setText('Deck to add: ')
        self.hboxlayout1.addWidget(self.label2)
        self.combox = QComboBox(self)
        threading.Thread(target=self.get_deckNames).start()
        self.hboxlayout1.addWidget(self.combox)
        self.add_botton = QPushButton(self)
        self.add_botton.setText('Add')
        self.add_botton.clicked.connect(self.on_click_add)
        self.hboxlayout1.addWidget(self.add_botton)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.hboxlayout2 = QHBoxLayout(self)
        self.label3 = QLabel(self)
        self.label3.setText('Current media save direction: ')
        self.hboxlayout2.addWidget(self.label3)
        self.lineEdit2 = QLineEdit(self)
        if 'media_dir' in self.config:
            self.lineEdit2.setText(self.config['media_dir'])
        else:
            self.lineEdit2.setText(self.path)
            self.config['media_dir'] = self.path
        self.hboxlayout2.addWidget(self.lineEdit2)
        self.media_dir_botton = QPushButton(self)
        self.media_dir_botton.setText('Confirm Change')
        self.media_dir_botton.clicked.connect(self.on_click_media_dir)
        self.hboxlayout2.addWidget(self.media_dir_botton)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.webview = QWebEngineView(self)
        with open(self.path+'word.html', 'w') as f:
            f.write('<!DOCTYPE html><html><head><style>body{background-color:')
            f.write(self.back_ground_color)
            f.write(';color:')
            f.write(self.text_color)
            f.write(';}</style></head><body><h1 style="text-align:center;">Welcome to Binki!</h1>&nbsp;&nbsp;&nbsp;&nbsp;search to view the new card and then you can add it.</body></html>')
        self.webview.load(
            QUrl.fromLocalFile(self.path+'word.html'))
        self.vboxlayout.addWidget(self.webview)

    def on_click_search(self):
        word_name = self.lineEdit1.text()
        if not word_name:
            return
        if not self.lock.acquire(blocking=False):
            return
        self.lineEdit1.clear()
        with open(self.path+'word.html', 'w') as f:
            f.write('<!DOCTYPE html><html><head><style>body{background-color:')
            f.write(self.back_ground_color)
            f.write(';color:')
            f.write(self.text_color)
            f.write(
                ';}</style></head><body><h1 style="text-align:center;">Searching and Downloading... Please wait.</h1></body></html>')
        self.webview.load(
            QUrl.fromLocalFile(self.path+'word.html'))
        threading.Thread(target=self.build_html, args=[word_name]).start()

    def on_click_add(self):
        if not self.word:
            showInfo('Please search for a word to add first!', parent=self)
            return
        if not self.combox.currentText():
            showInfo('Please select a deck to add card to it!', parent=self)
            return
        if not self.lock.acquire(blocking=False):
            showInfo('Please wait search complete!', parent=self)
            return
        threading.Thread(target=self.add_word).start()

    def add_word(self):
        modelNames = {
            "action": "modelNames",
            "version": 6
        }
        modelNames = self.invoke(modelNames)['result']
        if 'Bing Dictionary' not in modelNames:
            createModel = {
                "action": "createModel",
                "version": 6,
                "params": {
                    "modelName": "Bing Dictionary",
                    "inOrderFields": ["Word", "Front", "Back"],
                    "cardTemplates": [
                        {
                            "Name": "Card 1",
                            "Front": "{{Front}}",
                            "Back": "{{FrontSide}}\r\n<hr id=answer>\r\n{{Back}}"
                        }
                    ]
                }
            }
            result = self.invoke(createModel)
            if result['error']:
                showInfo("Can't create note model, you may create it yourself" +
                         '\r\n'+result['error']+'\r\n'+json.dumps(createModel), parent=self)
        with open(self.path+'front.html', 'r') as f:
            front = f.read()
        with open(self.path+'back.html', 'r') as f:
            back = f.read()
        addNote = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": self.combox.currentText(),
                    "modelName": "Bing Dictionary",
                    "fields": {
                        "Word": self.word.word,
                        "Front": front,
                        "Back": back
                    },
                    "options": {
                        "allowDuplicate": False,
                        "duplicateScope": "deck",
                        "duplicateScopeOptions": {
                            "deckName": self.combox.currentText(),
                            "checkChildren": False,
                            "checkAllModels": False
                        }
                    },
                    "tags": [
                        "Bing Dictionary"
                    ]
                }
            }
        }
        result = self.invoke(addNote)
        if result['error']:
            with open(self.path+'word.html', 'w') as f:
                f.write(
                    '<!DOCTYPE html><html><head><style>body{background-color:')
                f.write(self.back_ground_color)
                f.write(';color:')
                f.write(self.text_color)
                f.write(
                    ';}</style></head><body><h1 style="text-align:center;">Add word with error!</h1></body><div>'+result['error']+'</div></html>')
        else:
            with open(self.path+'word.html', 'w') as f:
                f.write(
                    '<!DOCTYPE html><html><head><style>body{background-color:')
                f.write(self.back_ground_color)
                f.write(';color:')
                f.write(self.text_color)
                f.write(
                    ';}</style></head><body><h1 style="text-align:center;">Add word successfully! New card\'s ID: '+str(result['result'])+'</h1></body></html>')
        self.done_signal.emit('add complete')
        pass

    def on_click_media_dir(self):
        self.config['media_dir'] = self.lineEdit2.text()
        with open(self.path+'config.json', 'w') as f:
            f.write(json.dumps(self.config))

    def update_html(self, type):
        if type == 'search complete':
            self.webview.load(
                QUrl.fromLocalFile(self.path+'word.html'))
            if self.word.errs_num != 0:
                err_title = str(self.word.errs_num) + \
                    'errors' if self.word.errs_num > 1 else 'error'
                err_title += '\r\n'
                err_info = ''
                for err in self.word.errs_logs:
                    err_info += err+'\r\n'
                showInfo(err_title+'\r\n'+err_info, parent=self)
            self.lock.release()
        elif type == 'add complete':
            self.word = ''
            self.webview.load(
                QUrl.fromLocalFile(self.path+'word.html'))
            self.lock.release()

    def request(self, action):
        if 'params' in action:
            return {'action': action['action'], 'params': action['params'], 'version': 6}
        else:
            return {'action': action['action'], 'version': 6}

    def invoke(self, action):
        requestJson = json.dumps(self.request(action)).encode('utf-8')
        response = json.load(urllib.request.urlopen(
            urllib.request.Request('http://localhost:'+str(self.config['webBindPort']), requestJson)))
        return response

    def get_deckNames(self):
        deckNames = {
            "action": "deckNames",
            "version": 6
        }
        self.deckNames = self.invoke(deckNames)['result']
        for deckName in self.deckNames:
            self.combox.addItem(deckName)
        self.combox.setCurrentIndex(0)

    def build_html(self, word_name):
        if not self.word or self.word.word != word_name:
            self.word = BingDict_Word(word_name, self.config['media_dir'])
            self.word.get_all()
        f_w = open(self.path+'word.html', 'w')
        f_f = open(self.path+'front.html', 'w')
        html_string = '<!DOCTYPE html><html><head><style>body {background-color:'
        html_string += self.back_ground_color+';color:'
        html_string += self.text_color+';'
        f_w.write(html_string+'font-family: arial;' +
                  'font-size: 20px;' + 'text-align: center;')
        f_f.write(html_string)
        html_string = '}</style></head><body><h1>'
        html_string += self.word.word+'</h1>'
        f_w.write(html_string)
        f_f.write(html_string)

        if self.word.phonetic_symbol_US or self.word.phonetic_symbol_EN:
            f_w.write('<div>')
            f_f.write('<div>')
            if self.word.phonetic_symbol_US:
                f_w.write('<a>' + self.word.phonetic_symbol_US+'</a>')
                f_f.write('<a>' + self.word.phonetic_symbol_US+'</a>')
            if self.word.pronunciation_US:
                f_w.write('<span><audio controls style="height: 20px; width: 20px;" src=' + '"' +
                          self.config['media_dir']+self.word.pronunciation_US+'"'+' autoplay></span>')
                f_f.write(
                    '<span>[sound:'+self.word.pronunciation_US+']</span>')
            if self.word.phonetic_symbol_EN:
                f_w.write('<a>' + self.word.phonetic_symbol_EN+'</a>')
                f_f.write('<a>' + self.word.phonetic_symbol_EN+'</a>')
            if self.word.pronunciation_EN:
                f_w.write('<span><audio controls style="height: 20px; width: 20px;" src=' + '"' +
                          self.config['media_dir']+self.word.pronunciation_EN+'"'+' autoplay></span>')
                f_f.write(
                    '<span>[sound:'+self.word.pronunciation_EN+']</span>')
        f_w.write('</div>')
        f_f.write('</div></body></html>')
        f_f.close()

        f_b = open(self.path+'back.html', 'w')
        f_b.write(
            '<!DOCTYPE html><html><head><style>body {background-color:')
        f_b.write(self.back_ground_color)
        f_b.write(';color:')
        f_b.write(self.text_color)
        f_b.write('}</style></head><body>')

        if self.word.word_image:
            f_w.write('<div>')
            f_b.write('<div>')
            for img in self.word.word_image:
                f_w.write('<img src="'+self.config['media_dir']+img+'">')
                f_b.write('<img src="'+img+'">')
            f_b.write('</div>')
            f_w.write('</div>')

        if self.word.meaning_summary:
            f_w.write(
                '<div style="text-align: left;margin-left: 5%;">词义总结:<div style="text-align: left;margin-left: 5%;font-size: medium;">')
            f_b.write(
                '<div style="text-align: left;margin-left: 5%;">词义总结:<div style="text-align: left;margin-left: 5%;font-size: medium;">')
            for meaning in self.word.meaning_summary:
                f_w.write('<div><a>'+meaning['POS'] +
                          (' ' if meaning['POS'] != '网络' else ': '))
                f_b.write('<div><a>'+meaning['POS'] +
                          (' ' if meaning['POS'] != '网络' else ': '))
                f_w.write('</a><span>'+meaning['meaning']+'</span></div>')
                f_b.write('</a><span>'+meaning['meaning']+'</span></div>')
            f_w.write('</div></div>')
            f_b.write('</div></div')

        if self.word.word_transformation:
            f_w.write(
                '<div style="text-align: left;margin-left: 5%;">单词变形:<div style="text-align: left;margin-left: 5%;">')
            f_b.write(
                '<div style="text-align: left;margin-left: 5%;">单词变形:<div style="text-align: left;margin-left: 5%;">')
            for transformation in self.word.word_transformation:
                f_w.write('<span>'+transformation['transform type'] +
                          ': ' + '</span><a href="'+transformation['transformation link']+'">'+transformation['transformation']+' </a>')
                f_b.write('<span>'+transformation['transform type'] +
                          ': ' + '</span><a href="'+transformation['transformation link']+'">'+transformation['transformation']+' </a>')
            f_w.write('</div></div>')
            f_b.write('</div></div>')

        if self.word.collocate:
            f_w.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">搭配:')
            f_b.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">搭配:')
            for collocate in self.word.collocate:
                f_w.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          collocate['collocate type']+' </span>')
                f_b.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          collocate['collocate type']+' </span>')
                col = collocate['collocates'][0]
                f_w.write(
                    '<a href="'+col['collocate link']+'">'+col['collcate']+'</a>')
                f_b.write(
                    '<a href="'+col['collocate link']+'">'+col['collcate']+'</a>')
                if len(collocate['collocates']) > 1:
                    for col in collocate['collocates'][1:-1]:
                        f_w.write('<span>, </span>')
                        f_w.write(
                            '<a href="'+col['collocate link']+'">'+col['collcate']+'</a>')
                        f_b.write('<span>, </span>')
                        f_b.write(
                            '<a href="'+col['collocate link']+'">'+col['collcate']+'</a>')
                f_w.write('</div>')
                f_b.write('</div>')
            f_w.write('</div>')
            f_b.write('</div>')
        if self.word.synonym:
            f_w.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">同义词:')
            f_b.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">同义词:')
            for synonym in self.word.synonym:
                f_w.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          synonym['synonym type']+' </span>')
                f_b.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          synonym['synonym type']+' </span>')
                syn = synonym['synonyms'][0]
                f_w.write(
                    '<a href="'+syn['synonym link']+'">'+syn['synonym']+'</a>')
                f_b.write(
                    '<a href="'+syn['synonym link']+'">'+syn['synonym']+'</a>')
                if len(synonym['synonyms']) > 1:
                    for syn in synonym['synonyms'][1:-1]:
                        f_w.write('<span>, </span>')
                        f_w.write(
                            '<a href="'+syn['synonym link']+'">'+syn['synonym']+'</a>')
                        f_b.write('<span>, </span>')
                        f_b.write(
                            '<a href="'+syn['synonym link']+'">'+syn['synonym']+'</a>')
                f_w.write('</div>')
                f_b.write('</div>')
            f_w.write('</div>')
            f_b.write('</div>')

        if self.word.antonym:
            f_w.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">反义词:')
            f_b.write(
                '<div style="text-align: left;margin-left: 5%;font-size: medium;">反义词:')
            for antonym in self.word.antonym:
                f_w.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          antonym['antonym type']+' </span>')
                f_b.write('<div style="text-align: left;margin-left: 5%;"><span>' +
                          antonym['antonym type']+' </span>')
                ant = antonym['antonyms'][0]
                f_w.write(
                    '<a href="'+ant['antonym link']+'">'+ant['antonym']+'</a>')
                f_b.write(
                    '<a href="'+ant['antonym link']+'">'+ant['antonym']+'</a>')
                if len(antonym['antonyms']) > 1:
                    for ant in antonym['antonyms'][1:-1]:
                        f_w.write('<span>, </span>')
                        f_w.write(
                            '<a href="'+ant['antonym link']+'">'+ant['antonym']+'</a>')
                        f_b.write('<span>, </span>')
                        f_b.write(
                            '<a href="'+ant['antonym link']+'">'+ant['antonym']+'</a>')
                f_w.write('</div>')
                f_b.write('</div>')
            f_w.write('</div>')
            f_b.write('</div>')

        if self.word.Authoritative_English_Chinese_Dual_Explanation or self.word.Authoritative_English_Chinese_Dual_Explanation_info:
            f_w.write('<br>')
            f_b.write('<br>')
            f_w.write('<div style="text-align: left;margin-left: 5%;">权威英汉双解')
            f_b.write('<div style="text-align: left;margin-left: 5%;">权威英汉双解')
            for explanation in self.word.Authoritative_English_Chinese_Dual_Explanation:
                f_w.write('<div style="text-align: left;margin-left: 5%;">')
                f_b.write('<div style="text-align: left;margin-left: 5%;">')
                f_w.write('<a>'+explanation['POS']+'</a>')
                f_b.write('<a>'+explanation['POS']+'</a>')
                count = 0
                for expla in explanation['Explanations']:
                    if 'summary CN' in expla:
                        f_w.write(
                            '<div style="text-align: left;margin-left: 5%;font-size: large;"><a>'+expla['summary CN']+' </a>')
                        f_b.write(
                            '<div style="text-align: left;margin-left: 5%;font-size: large;"><a>'+expla['summary CN']+' </a>')
                        f_w.write('<a>'+expla['summary EN']+'</a></div>')
                        f_b.write('<a>'+expla['summary EN']+'</a></div>')
                    elif 'pattern' in expla:
                        count += 1
                        f_w.write(
                            '<div style="text-align: left;margin-left: 5%;font-size: medium;"><span>'+str(count)+'.&nbsp;&nbsp;</span>')
                        f_b.write(
                            '<div style="text-align: left;margin-left: 5%;font-size: medium;"><span>'+str(count)+'.&nbsp;&nbsp;</span>')
                        if expla['usage']:
                            f_w.write('<span style="color: red;">' +
                                      expla['usage']+'</span>')
                            f_b.write('<span style="color: red;">' +
                                      expla['usage']+'</span>')
                        if expla['pattern']:
                            f_w.write(
                                '<span>'+expla['pattern']+'&nbsp;&nbsp;</span>')
                            f_b.write(
                                '<span>'+expla['pattern']+'&nbsp;&nbsp;</span>')
                        f_w.write('<span>'+expla['detail CN'] +
                                  '&nbsp;&nbsp;</span><span>'+expla['detail EN']+'&nbsp;&nbsp;</span>')
                        f_b.write('<span>'+expla['detail CN'] +
                                  '&nbsp;&nbsp;</span><span>'+expla['detail EN']+'&nbsp;&nbsp;</span>')
                        if expla['infor']:
                            f_w.write('<span style="color: red;">' +
                                      expla['infor']+'</span>')
                            f_b.write('<span style="color: red;">' +
                                      expla['infor']+'</span>')
                        f_w.write('</div>')
                        f_b.write('</div>')

                if explanation['IDMs']:
                    f_w.write(
                        '<br>'+'<div style="text-align: left;border: groove;margin-left: 5%;"><a>IDM</a>')
                    f_b.write(
                        '<br>'+'<div style="text-align: left;border: groove;margin-left: 5%;"><a>IDM</a>')
                    for IDM in explanation['IDMs']:
                        f_w.write(
                            '<div style="font-size: large; margin-left: 5%;"><a>'+IDM['IDM'] +
                            '</a><div style="font-size: medium; margin-left: 5%;"><span>' +
                            IDM['meaning CN'] + '&nbsp;&nbsp;</span><span>'+IDM['meaning EN'] +
                            '&nbsp;&nbsp;</span>')
                        f_b.write(
                            '<div style="font-size: large; margin-left: 5%;"><a>'+IDM['IDM'] +
                            '</a><div style="font-size: medium; margin-left: 5%;"><span>' +
                            IDM['meaning CN'] + '&nbsp;&nbsp;</span><span>'+IDM['meaning EN'] +
                            '&nbsp;&nbsp;</span>')
                        if IDM['infor']:
                            f_w.write('<span style="color: red;">' +
                                      IDM['infor']+'</span>')
                            f_b.write('<span style="color: red;">' +
                                      IDM['infor']+'</span>')
                        f_w.write('</div></div>')
                        f_b.write('</div></div>')
                    f_w.write('</div>')
                    f_b.write('</div>')
                f_w.write('</div>')
                f_b.write('</div>')

            if self.word.Authoritative_English_Chinese_Dual_Explanation_info:
                f_w.write('<div style="text-align: left;margin-left: 5%;">'+self.word.Authoritative_English_Chinese_Dual_Explanation_info[
                          'info type']+' <a href="'+self.word.Authoritative_English_Chinese_Dual_Explanation_info['info']['link']+'">'+self.word.Authoritative_English_Chinese_Dual_Explanation_info['info']['content']+"</a></div>")
                f_b.write('<div style="text-align: left;margin-left: 5%;">'+self.word.Authoritative_English_Chinese_Dual_Explanation_info[
                          'info type']+' <a href="'+self.word.Authoritative_English_Chinese_Dual_Explanation_info['info']['link']+'">'+self.word.Authoritative_English_Chinese_Dual_Explanation_info['info']['content']+"</a></div>")
            f_w.write('</div>')
            f_b.write('</div>')

        if self.word.sentence:
            f_w.write('<br><div style="text-align: left;margin-left: 5%;">例句')
            f_b.write('<br><div style="text-align: left;margin-left: 5%;">例句')
            for sentence in self.word.sentence:
                f_w.write('<div style="font-size: medium; margin-left: 5%;">')
                f_b.write('<div style="font-size: medium; margin-left: 5%;">')

                f_w.write('<div>')
                f_b.write('<div>')
                for EN in sentence['EN']:
                    if EN['link']:
                        f_w.write(
                            '<a href="'+EN['link']+'">'+EN['word']+'</a>')
                        f_b.write(
                            '<a href="'+EN['link']+'">'+EN['word']+'</a>')
                    else:
                        f_w.write('<span>'+EN['word']+'</span>')
                        f_b.write('<span>'+EN['word']+'</span>')
                f_w.write('</div>')
                f_b.write('</div>')

                f_w.write('<div style="margin-bottom: 10px;">')
                f_b.write('<div>')
                for CN in sentence['CN']:
                    if CN['link']:
                        f_w.write(
                            '<a href="'+CN['link']+'">'+CN['word']+'</a>')
                        f_b.write(
                            '<a href="'+CN['link']+'">'+CN['word']+'</a>')
                    else:
                        f_w.write('<span>'+CN['word']+'</span>')
                        f_b.write('<span>'+CN['word']+'</span>')
                if sentence['audio']:
                    if sentence['audio source']:
                        f_w.write('<a href="'+sentence['audio source']['link'] +
                                  '">'+sentence['audio source']['name']+'</a>')
                        f_b.write('<a href="'+sentence['audio source']['link'] +
                                  '">'+sentence['audio source']['name']+'</a>')
                    f_w.write('<audio controls style="height: 20px; width: 20px;" src=' + '"' +
                              self.config['media_dir']+sentence['audio']+'"'+'>')
                    f_b.write('[sound:'+sentence['audio']+']')
                f_w.write('</div>')
                f_b.write('</div>')

                f_w.write('</div>')
                f_b.write('</div>')
            f_w.write('</div>')
            f_b.write('</div>')

        f_b.write('</body></html>')
        f_w.write('</body></html>')
        f_b.close()
        f_w.close()
        self.done_signal.emit('search complete')
