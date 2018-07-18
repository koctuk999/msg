#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from socket import socket,AF_INET,SOCK_DGRAM
import sys
from random import randint
from datetime import datetime
import pickle
from threading import Thread
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,\
    QGridLayout,QLabel,QTextEdit,QLineEdit,QMessageBox,QFrame
from PyQt5.QtCore import QThread,pyqtSignal
import os
f=False #флаг закрытия

class recv_msg(QThread):
    """Поток для приёма сообщений"""
    rm = pyqtSignal(list)
    def __init__(self):
        super().__init__()
    def run(self):

        sock = socket(AF_INET,SOCK_DGRAM)#UDP сокет
        host = '' #хост для всех интерфейсов
        port = 9090
        sock.bind((host, port))#связываем хост и порт
        while True:
            data, addr =sock.recvfrom(1024)#приём данных по 1кБ
            data=pickle.loads(data)#распаковка
            data.append(addr[0])
            self.rm.emit(data)
            if f: #если флаг установлен -
                sock.close() #закрытие сокета
                break#выход из цикла

class Example(QWidget):
    """Окно приложения"""
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
    def initUI(self):
        grid=QGridLayout()
        self.ed_ip=QLineEdit()#ввод ip
        self.ed_ip.setFixedSize(self.ed_ip.sizeHint())
        self.ed_ip.setToolTip('<i>Введите IP и нажмите ENTER</i>')
        self.ed_msg=QLineEdit("Введите сообщение",self)
        self.rec_msg = QTextEdit()#ввод сообщения для отправки
        self.rec_msg.setReadOnly(True)
        self.btn_send=QPushButton("Отправить",self)#кнопка отправки
        self.btn_send.setEnabled(False)
        self.btn_send.setFixedSize(self.btn_send.sizeHint())
        self.btn_send.setToolTip('Чтобы активировать кнопку введите IP')
        self.ed_ip.editingFinished.connect(self.btnen)  # сигнал-проверка ip
        self.btn_send.clicked.connect(self.sendmsg)#сигнал клика
        lab1=QLabel('<b>IP-получателя</b>',self)
        lab1.setFixedSize(lab1.sizeHint())
        lab2=QLabel('<b>Исходящее cообщение</b>',self)
        lab2.setFixedSize(lab2.sizeHint())
        lab3=QLabel('<b>Чат</b>',self)
        lab3.setFixedSize(lab3.sizeHint())
        lab4=QLabel("<b>Доступность: </b>",self)
        self.ind=QFrame(self)
        self.ind.setFrameShape(QFrame.StyledPanel)
        self.ind.setFixedSize(7,7)
        self.ind.setStyleSheet("background-color: red")
        grid.addWidget(self.ed_ip,1,0)
        grid.addWidget(lab4,1,1)
        grid.addWidget(self.ind,1,2)
        grid.addWidget(self.ed_msg,3,0,1,3)
        grid.addWidget(self.btn_send,4,0)
        grid.addWidget(lab1,0,0)
        grid.addWidget(lab2,2,0)
        grid.addWidget(lab3,5,0)
        grid.addWidget(self.rec_msg,6,0,5,8)
        self.setLayout(grid)
        self.setWindowTitle("Simple-chat")
        self.setFixedSize(380,500)
        self.setStyleSheet("background-color: #3399FF; color: #000033")
        self.setWindowOpacity(0.9)
        self.ed_ip.setStyleSheet("background-color: #33CCFF")
        self.rec_msg.setStyleSheet("background-color: #33CCFF")
        self.ed_msg.setStyleSheet("background-color: #33CCFF")
        self.btn_send.setStyleSheet("background-color: #33FFFF")
        self.show()
        self.thread=recv_msg()
        self.thread.rm.connect(self.recmsg)
        self.thread.start()#старт потока приёма
    def btnen(self):
        """Слот-проверка ip адреса"""
        ip=self.ed_ip.text().split('.')
        try:
            for i in ip: i=int(i)
            if len(ip)== 4:
                resp=os.system("ping -c 1 -i 0.2 " + ".".join(ip)) #Проверка доступности
                if resp == 0:
                    self.btn_send.setEnabled(True)
                    self.ind.setStyleSheet("background-color: #00FF00")
                else:
                    self.ind.setStyleSheet("background-color: #CC3333")
            else:
                self.btn_send.setEnabled(False)
                self.ind.setStyleSheet("background-color: #CC3333")
        except ValueError:
            self.btn_send.setEnabled(False)
            self.ind.setStyleSheet("background-color: #CC3333")
    def sendmsg(self):
        """Слот-отправление сообщения"""
        sock=socket(AF_INET, SOCK_DGRAM) #создание сокета
        host=self.ed_ip.text() #адрес получателя
        port=9090 #порт получателя
        addr=(host,port)
        text=self.ed_msg.text()
        id=randint(1,10000)
        t=str(datetime.now(tz=None)).split(" ")[1].split(".")[0] #преобразование времени ЧЧ:ММ:СС
        data=[id,t,text]
        self.rec_msg.append("Я:{0}".format(text))
        sock.sendto(pickle.dumps(data), addr)
    def recmsg(self,value):

     QMessageBox.information(self,'Информация','Новое сообщение от {0}'
     ' \n Время отправки: {1} \n Идентификатор: {2}'.format(value[3],value[1],value[0]))
     self.rec_msg.append("<b style=color:#ff0000>{0}</b>({1}): <i>{2}</i>".format(
        value[3],value[1],value[2]))#добавление данных в TextEdit
    def closeEvent(self,event):
        """Закрытие приложения"""
        reply = QMessageBox.question(self, 'Message', "Вы точно хотите выйти?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            f = True
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())