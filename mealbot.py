# 안동 중앙고등학교 Telegram 급식봇
# Developer : 안재범
# 윈도우 환경에서는 오류납니다. 무조건 리눅스 환경에서만...!
#
# 초기설정
# pip3 install python-telegram-bot
# pip3 install requests library
# pip3 install BeautifulSoup4 library
# pip3 install regex library
# pip3 install datetime (업데이트 위함)
#
# 실행전 봇에 아무 메시지를 보낸후 실행해야 오류 안남
# 로그기능을 원치 않는다면 로그 용량 확인및 초기화 기능과 전교회장 및 개발자에게 건의와 로그 불러오기, 로그제거 코드 제거하면 됨

import telegram
import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import random
import urllib
import urllib3
import re
from parser import *
import datetime
from pytz import timezone
import time
from datetime import date, timedelta

from urllib.request import urlopen
from bs4 import BeautifulSoup

meal_token = '봇 api 키를 입력하세요'   #토큰을 변수에 저장합니다.

#봇 선언
bot = telegram.Bot(token = meal_token)

#커스텀 키보드 설정
custom_keyboard = [
        ["/help", "정보", "공유하기!"],
        ["어제 급식", "오늘 급식", "내일 급식"],
        ["이틀뒤 급식", "3일뒤 급식", "4일뒤 급식"],
        ]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

#챗 아이디 설정
# updates = bot.getUpdates()
# chat_id = updates[-1].message.chat.id

#커스텀 키보드 설정
bot.send_message(chat_id=79673869, text="Start 안동 중앙고등학교 급식봇, 커스텀 키보드 설정완료!",  reply_markup=reply_markup)

#시간설정
n = time.localtime().tm_wday
now = datetime.datetime.now()
file = open("playnom.txt", 'w')
file.write("0")
file.close()

#초기설정 성공 안내
print("Start 안동 중앙고등학교 급식봇")

#도움말
def help_command(bot, update) :
    file = open("notice.txt", 'r')
    aaa=file.read()
    file.close()
    update.message.reply_text("급식봇 도움말\n이 봇은 안동 중앙고등학교의 급식을 알려주는 봇입니다.\n\n<공지>\n%s" %aaa, reply_markup=reply_markup)
    update.message.reply_text("모든 명령어 : \n\n*봇 관련\n/start - 환영인사\n/help - 이 도움말을 표시합니다.\n정보 - 안동 중앙고등학교 급식봇의 정보를 알려드립니다.\n\n*급식\n어제 급식 - 어제의 급식을 알려드립니다.\n오늘 급식 - 오늘의 급식을 알려드립니다.\n내일 급식 - 내일의 급식을 알려드립니다.\n이틀뒤 급식 - 이틀뒤 급식을 알려드립니다.\n3일뒤 급식 - 3일뒤 급식을 알려드립니다.\n4일뒤 급식 - 4일뒤 급식을 알려드립니다.\n\n*학교\n중앙고 - 안동 중앙고등학교 사이트 링크를 전송합니다.\n경덕중 - 경덕중학교 사이트 링크를 전송합니다.\n\n*포털사이트 바로가기\n구글 - 구글 링크를 전송합니다.\n네이버 - 네이버 링크를 전송합니다.\n다음 - 다음 링크를 전송합니다.\n프로톤 메일 - 프로톤메일 링크를 전송합니다.\n깃허브 - 깃허브 링크를 전송합니다.\n페이스북 - 페이스북 링크를 전송합니다.\n인스타 - 인스타그램 링크를 전송합니다.\n\n*시간, 날짜\n날짜 - 오늘의 날짜를 알려줍니다.\n시간 - 현재 시간을 알려줍니다.")

def start_command(bot, update) :
    update.message.reply_text("안녕하세요! 안동 중앙고등학교 급식봇 입니다.\n도움말을 보시려면 /help << 이 문자를 눌러주세요!\n급식관련은 제가만든 새 키보드를 확인하세요!", reply_markup=reply_markup)

#일반 메시지
def get_message(bot, update) :
    file = open("day.txt", 'r')
    dday=file.read()
    file.close()
    today = date.today()
    if not dday==today.strftime('%Y.%m.%d'):
        update.message.reply_text("서버에 급식 데이터 다운로드중. . .\n이전 데이터베이스 버전 : %s" %dday)

        now = datetime.datetime.now()
        n = time.localtime().tm_wday
        
        #데이터베이스 버전 업데이트
        file = open("day.txt", 'w')
        file.write(today.strftime('%Y.%m.%d'))
        file.close()

        #어제 급식 다운로드
        yester = date.today() - timedelta(1)
        if n==0:
            r=6
        else:
            r=n-1
        meal1 = get_diet(1, yester.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, yester.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, yester.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("yester.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n어제 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, yester.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #오늘 급식 다운로드
        r=n
        meal1 = get_diet(1, today.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, today.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, today.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("today.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n오늘 급식(%s년 %s월 %s일)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day,now.year, now.month, now.day, meal1, meal2, meal3))
        file.close()

        #내일 급식 다운로드
        tomorrow = date.today() + timedelta(1)
        if n==6:
            r=0
        else:
            r=n+1
        meal1 = get_diet(1, tomorrow.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, tomorrow.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, tomorrow.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("tomorrow.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, tomorrow.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #이틀뒤 급식 다운로드
        two = date.today() + timedelta(2)
        if n==5:
            r=0
        elif n==6:
            r=1
        else:
            r=n+2
        meal1 = get_diet(1, two.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, two.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, two.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("2.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, two.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #3일뒤 급식 저장
        three = date.today() + timedelta(3)
        if n==4:
            r=0
        elif n==5:
            r=1
        elif n==6:
            r=2
        else:
            r=n+3
        meal1 = get_diet(1, three.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, three.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, three.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("3.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n3일뒤 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, three.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #4일뒤 급식 저장
        four = date.today() + timedelta(4)
        if n==3:
            r=0
        elif n==4:
            r=1
        elif n==5:
            r=2
        elif n==6:
            r=3
        else:
            r=n+4
        meal1 = get_diet(1, four.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, four.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, four.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("4.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n4일뒤 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, four.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        update.message.reply_text("급식 데이터 다운로드 완료!")
        print ("급식 데이터가 업데이트됨 - 현재 급식 데이터베이스 버전 : %s" %today.strftime('%Y.%m.%d'))



    #어제 급식
    if update.message.text[0:2]=="어제":
        file = open("yester.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)
        
    #오늘 급식
    elif update.message.text[0:2]=="오늘":
        file = open("today.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #내일 급식
    elif update.message.text[0:2]=="내일":
        file = open("tomorrow.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #이틀뒤 급식
    if update.message.text[0:3]=="이틀뒤":
        file = open("2.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #3일뒤 급식
    elif update.message.text[0:3]=="3일뒤":
        file = open("3.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #4일뒤 급식
    elif update.message.text[0:3]=="4일뒤":
        file = open("4.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #급식관련
    elif update.message.text=="급식":
        update.message.reply_text("어제, 오늘, 내일, 이틀뒤, 3일뒤, 4일뒤 급식중에 무엇을 알려드릴까요? 아래 키보드중 하나를 눌러주세요.", reply_markup=reply_markup)

    #정보 information
    elif update.message.text[0:2]=="정보":
        file = open("day.txt", 'r')
        dday=file.read()
        file.close()
        #최초개발자 수정 금지
        update.message.reply_text("<안동 중앙고등학교 급식봇 정보>\n\n급식 데이터베이스 : %s\n최초 개발자 : 안재범(2003) (https://github.com/NewPremium)" %(dday))

    #끝말잇기
    elif update.message.text[0:2]=="끝말":
        update.message.reply_text("네, 저부터 시작할게요.")
        file = open("playnom.txt", 'r')
        playnom=file.read()
        file.close()
        if playnom=="0":
            update.message.reply_text("나무꾼!")
            file = open("playnom.txt", 'w')
            file.write("1")
            file.close()
        elif playnom=="1":
            update.message.reply_text("과녁!")
            file = open("playnom.txt", 'w')
            file.write("2")
            file.close()
        elif playnom=="2":
            update.message.reply_text("해질녘!")
            file = open("playnom.txt", 'w')
            file.write("3")
            file.close()
        elif playnom=="3":
            update.message.reply_text("기쁨!")
            file = open("playnom.txt", 'w')
            file.write("4")
            file.close()
        elif playnom=="4":
            update.message.reply_text("동녘!")
            file = open("playnom.txt", 'w')
            file.write("5")
            file.close()
        elif playnom=="5":
            update.message.reply_text("몽쉘!")
            file = open("playnom.txt", 'w')
            file.write("6")
            file.close()
        elif playnom=="6":
            update.message.reply_text("새벽녘!")
            file = open("playnom.txt", 'w')
            file.write("7")
            file.close()
        elif playnom=="7":
            update.message.reply_text("로켓!")
            file = open("playnom.txt", 'w')
            file.write("8")
            file.close()
        elif playnom=="8":
            update.message.reply_text("히읗!")
            file = open("playnom.txt", 'w')
            file.write("0")
            file.close()

    #날짜와 시간
    elif update.message.text[0:2]=="날짜":
        now = datetime.datetime.now()
        update.message.reply_text("오늘의 날짜 : \n%s년 %s월 %s일 입니다." %(now.year,now.month, now.day))

    elif update.message.text[0:2]=="시간":
        now = datetime.datetime.now()
        update.message.reply_text("현재 시간 : \n%s시 %s분 %s초 입니다." %(now.hour,now.minute, now.second))

    #포털 사이트
    elif update.message.text[0:2]=="구글" or update.message.text[0:6]=="google" or update.message.text[0:6]=="Google":
        update.message.reply_text("Google\nhttps://www.google.com/")
    elif update.message.text[0:3]=="네이버" or update.message.text[0:5]=="naver" or update.message.text[0:5]=="Naver":
        update.message.reply_text("Naver\nhttps://www.naver.com/")
    elif update.message.text[0:3]=="깃허브" or update.message.text[0:6]=="github" or update.message.text[0:6]=="Github":
        update.message.reply_text("Github\nhttps://github.com/")
    elif update.message.text[0:2]=="다음" or update.message.text[0:4]=="daum" or update.message.text[0:4]=="Daum":
        update.message.reply_text("Daum\nhttps://www.daum.net/")
    elif update.message.text[0:3]=="프로톤" or update.message.text[0:6]=="proton" or update.message.text[0:6]=="Proton":
        update.message.reply_text("Proton mail\nhttps://protonmail.com/")
    elif update.message.text[0:3]=="파파고" or update.message.text[0:6]=="papago" or update.message.text[0:6]=="Papago":
        update.message.reply_text("Papago\nhttps://papago.naver.com/")
    elif update.message.text[0:4]=="페이스북" or update.message.text[0:8]=="facebook" or update.message.text[0:8]=="Facebook":
        update.message.reply_text("Facebook\nhttps://www.facebook.com/")
    elif update.message.text[0:3]=="인스타" or update.message.text[0:6]=="insta" or update.message.text[0:6]=="Insta":
        update.message.reply_text("인스타그램\nhttps://www.instagram.com/")

    #기본 대화
    elif update.message.text[0:2]=="안녕" or update.message.text[0:5]=="hello" or update.message.text[0:5]=="Hello" or update.message.text[0:2]=="hi" or update.message.text[0:2]=="Hi" or update.message.text[0:2]=="HI":
        update.message.reply_text("안녕하세요! 전 안동 중앙고등학교 급식봇입니다!")
    elif update.message.text[0]=="넌":
        update.message.reply_text("전 안동 중앙고등학교 급식봇이라 합니다!")
    elif update.message.text[0:3]=="경덕중":
        update.message.reply_text("경덕중학교 공식사이트\nhttp://school.gyo6.net/adgd/")
    elif update.message.text[0:3]=="중앙고":
        update.message.reply_text("안동 중앙고등학교 공식사이트\nhttp://school.gyo6.net/adja") 
    elif update.message.text[0:2]=="공유":
        update.message.reply_text("아래 링크를 복사하여 친구에게 공유하세요.\n상대방이 Telegram이 설치된 상태여야 합니다.\n\nhttps://t.me/jungangbot")

    #chat_id 알려주기
    elif update.message.text[0:2]=="id":
        update.message.reply_text("chat_id 체크중. . .")
        updates = bot.getUpdates()
        chat_id = updates[-1].message.chat.id
        update.message.reply_text("당신의 chat_id 는 %s 입니다." %chat_id)

    elif update.message.text=="공지":
        file = open("notice.txt", 'r')
        aaa=file.read()
        file.close()
        update.message.reply_text("<공지>\n%s" %aaa)

    #식단 업데이트
    elif update.message.text[0:4]=="업데이트" or update.message.text[0:4]=="새로고침":
        update.message.reply_text("서버에 급식 데이터 다운로드중. . .\n이전 데이터베이스 버전 : %s" %dday)
        today = date.today()
        now = datetime.datetime.now()
        n = time.localtime().tm_wday
        
        #데이터베이스 버전 업데이트
        file = open("day.txt", 'w')
        file.write(today.strftime('%Y.%m.%d'))
        file.close()

        #어제 급식 다운로드
        yester = date.today() - timedelta(1)
        if n==0:
            r=6
        else:
            r=n-1
        meal1 = get_diet(1, yester.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, yester.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, yester.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("yester.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n어제 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, yester.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #오늘 급식 다운로드
        r=n
        meal1 = get_diet(1, today.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, today.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, today.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("today.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n오늘 급식(%s년 %s월 %s일)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day,now.year, now.month, now.day, meal1, meal2, meal3))
        file.close()

        #내일 급식 다운로드
        tomorrow = date.today() + timedelta(1)
        if n==6:
            r=0
        else:
            r=n+1
        meal1 = get_diet(1, tomorrow.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, tomorrow.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, tomorrow.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("tomorrow.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, tomorrow.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #이틀뒤 급식 다운로드
        two = date.today() + timedelta(2)
        if n==5:
            r=0
        elif n==6:
            r=1
        else:
            r=n+2
        meal1 = get_diet(1, two.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, two.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, two.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("2.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, two.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #3일뒤 급식 저장
        three = date.today() + timedelta(3)
        if n==4:
            r=0
        elif n==5:
            r=1
        elif n==6:
            r=2
        else:
            r=n+3
        meal1 = get_diet(1, three.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, three.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, three.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("3.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n3일뒤 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, three.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        #4일뒤 급식 저장
        four = date.today() + timedelta(4)
        if n==3:
            r=0
        elif n==4:
            r=1
        elif n==5:
            r=2
        elif n==6:
            r=3
        else:
            r=n+4
        meal1 = get_diet(1, four.strftime('%Y.%m.%d'), r)
        meal2 = get_diet(2, four.strftime('%Y.%m.%d'), r)
        meal3 = get_diet(3, four.strftime('%Y.%m.%d'), r)
        if meal1==" ":
            meal1="급식이 없습니다."
        elif meal2==" ":
            meal2="급식이 없습니다."
        elif meal3==" ":
            meal3="급식이 없습니다."
        else:
            meal1=meal1
            meal2=meal2
            meal3=meal3
        file = open("4.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n4일뒤 급식(%s)\n조식 :\n\n%s\n\n중식 :\n\n%s\n\n석식 :\n\n%s" %(now.year, now.month, now.day, four.strftime('%Y년 %m월 %d일'), meal1, meal2, meal3))
        file.close()

        update.message.reply_text("급식 데이터 다운로드 완료!")
        print ("급식 데이터가 업데이트됨 - 현재 급식 데이터베이스 버전 : %s" %today.strftime('%Y.%m.%d'))

updater = Updater(meal_token)

message_handler = MessageHandler(Filters.text, get_message)
updater.dispatcher.add_handler(message_handler)

help_handler = CommandHandler('help', help_command)
updater.dispatcher.add_handler(help_handler)

start_handler = CommandHandler('start', start_command)
updater.dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()
