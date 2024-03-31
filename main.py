import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tkinter as tk
import requests

# from PIL import Image, ImageTk
# from io import BytesIO
import urllib
import urllib.request

from bs4 import BeautifulSoup
import tensorflow
import keras
import re
import webbrowser
import os
import urllib.request
from PIL import ImageTk, Image
from wordcloud import WordCloud
from konlpy.tag import Okt
from keras.preprocessing.text import Tokenizer
from textTrain import tok
from datetime import datetime
from Review import *

root = tk.Tk()
root.title('최신 영화 리뷰')
root.minsize(800, 450)  # 최소 사이즈
root.resizable(False, False)

'''1. 프레임 생성'''
# 우측 프레임 (LabelFrame)
frm1 = tk.LabelFrame(root, text="영화 리뷰", pady=15, padx=15)  # pad 내부
frm1.grid(row=2, column=1, columnspan=2, pady=10, padx=10, sticky="nswe")  # pad 내부

# 우측 하단 프레임 (Frame)
frm2 = tk.Frame(root, pady=10)
frm2.grid(row=3, column=1, columnspan=2, pady=10)

# 좌측 프레임 (LabelFrame)
frm3 = tk.LabelFrame(root, text="영화 선택", pady=15, padx=15)  # pad 내부
frm3.grid(row=2, column=0, pady=10, padx=10, sticky="nswe")  # pad 내부

# 좌측 하단 프레임 (LabelFrame)
frm4 = tk.Frame(root)
frm4.grid(row=3, column=0)

# 좌측 프레임 (LabelFrame)-상단 영화 사진
frm5 = tk.LabelFrame(root, text="영화 사진", pady=15, padx=15)  # pad 내부
frm5.grid(row=0, column=0, pady=10, padx=10, sticky="nswe")  # pad 내부

# 좌측 하단 프레임 (LabelFrame)
frm6 = tk.Frame(root)
frm6.grid(row=1, column=0)

# 우측 프레임 (LabelFrame)-상단 영화 상세
frm7 = tk.LabelFrame(root, text="영화 상세", pady=15, padx=15)  # pad 내부
frm7.grid(row=0, column=1, pady=10, padx=10, sticky="nswe")  # pad 내부

# 우측 하단 프레임 (LabelFrame)
frm8 = tk.Frame(root)
frm8.grid(row=1, column=1)

# 우측 프레임 (LabelFrame)-상단 영화 상세검색
frm9 = tk.LabelFrame(root, text="영화 검색", pady=15, padx=15)  # pad 내부
frm9.grid(row=0, column=2, pady=10, padx=10, sticky="nswe")  # pad 내부

# 우측 하단 프레임 (LabelFrame)
frm10 = tk.Frame(root)
frm10.grid(row=1, column=2)

# 스크롤바 프레임
frmScroll = tk.Frame(frm3)

tagger = Okt()


def ko_tokenize(text, pos=['Noun', 'Verb', 'Adjective', 'Adverb', 'Exclamation', 'Unknown', 'KoreanParticle']):
    return [morph for morph, tag in tagger.pos(text) if tag in pos]


max_len = 30

movieCode = {"닥터 스트레인지: 대혼돈의 멀티버스": "182016", "날씨의 아이": "181114", "앵커": "190374", "신비한 동물들과 덤블도어의 비밀": "164122",
             "니 부모 얼굴이 보고 싶다": "159812", "피아니스트의 전설": "29059", "벤허": "10058", "파수꾼": "75378", "코다": "201073",
             "와이키키 브라더스": "31422", "피의 연대기": "164104", "비긴 어게인": "96379", "개를 훔치는 완벽한 방법": "112040", "중경삼림": "17059",
             "찬실이는 복도 많지": "189624", "바닷마을 다이어리": "132610", "귀향": "49302", "세자매": "193328", "안경": "69024",
             "라라랜드": "134963", "공기살인": "196362", "범죄도시2": "192608", "쥬라기월드: 도미니언": "191646", "그대가 조국": "216100"}


rnn_model = tensorflow.keras.models.load_model('movie_rnn_best_model.h5')


def searchMovieReview(setMovieCode):
    # 텍스트마이닝 강의자료(04 웹 문서 수집 및 HTML 파싱.ipynb)의 함수 인용
    pageNumbers = list(range(1, 3))  # 한 페이지에 10개의 리뷰가 나타남. 100여개의 리뷰 수집
    MovieReviewList = list()
    movieName = ""

    if setMovieCode == "0":  # 현재상영작 리스트에서 가져왔을때
        movieName = listbox9.get(listbox9.curselection())  # 리스트박스에서 선택한 항목 가져오기
        query = movieCode[movieName]  # 리스트박스에서 선택한 항목을 통해 movieCode 딕셔너리에서 고유 코드값을
    else:
        query = setMovieCode

    for i in pageNumbers:
        r = requests.get('https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=' + str(
            query) + '&target=after&page=' + str(i))
        # page= 에 들어가는 수를 바꿔줌으로써 리뷰 페이지를 이동하며 링크 수집
        # page= 에 들어가는 수를 바꿔줌으로써 리뷰 페이지를 이동하며 링크 수집
        soup = BeautifulSoup(r.content, 'html.parser')
        for div in soup.select('#old_content > table tbody tr td.title', limit=10):
            try:
                if div.select_one('br').next_sibling.strip() != "":  # 리뷰가 없이 평점만 있는 항목 제외
                    MovieReview = div.select_one('br').next_sibling.strip()  # 리뷰 내용 수집
                    MovieScore = div.find('em').get_text()  # 리뷰 평점 수집
                    MovieReviewList.append((MovieReview, MovieScore))  # 내용과 평점을 리스트에 추가
            except Exception as ex:
                print(ex)

    setMovieInfo(query)  # 영화 정보 세팅
    setMovieReviewList(MovieReviewList)  # 리뷰 리스트 세팅
    setReviewKeyword(movieName)  # 리뷰 키워드 세팅


def searchMovie():
    searchKeyword = lbl_search.get()
    global searchedMovie
    searchedMovie = list()
    r = requests.get('https://movie.naver.com/movie/search/result.naver?query=' + searchKeyword + '&section=all')
    soup = BeautifulSoup(r.content, 'html.parser')
    for div in soup.select('#old_content > ul:nth-child(4) > li'):
        try:
            movieName = div.select_one('dl > dt').get_text()  # 영화 제목
            movieLink = div.select_one('dl > dt > a')["href"]  # 영화 링크 (맨 뒤에 영화 코드가 있음)
            movieCode = movieLink[movieLink.index("code=") + 5:]  # 영화 코드
            searchedMovie.append([movieName, movieCode])

        except Exception as ex:
            print(ex)
    print(searchedMovie)
    txtListbox14.set(searchedMovie[0][0])
    txtListbox15.set(searchedMovie[1][0])
    txtListbox16.set(searchedMovie[2][0])
    txtListbox17.set(searchedMovie[3][0])
    txtListbox18.set(searchedMovie[4][0])


def setMovieInfo(query):  # 영화정보 세팅
    basicInfo = "장르 : "  # 영화정보
    # 영화정보 크롤링을 위한 requests
    info = requests.get('https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=' + str(
        query) + '&target=after&page=1')
    infoSoup = BeautifulSoup(info.content, 'html.parser')

    movieTitle = infoSoup.select_one('#old_content > div.choice_movie_box > div.choice_movie_info > h5 > a')[
        'title']  # 영화제목
    posterImgUrl = \
        infoSoup.select_one('#old_content > div.choice_movie_box > div.choice_movie_info > div.fl > a > img')[
            'src']  # 영화 포스터 이미지 링크

    urllib.request.urlretrieve(posterImgUrl, "moviePoster.jpg")  # 영화 포스터 이미지 저장

    for i in infoSoup.select_one('#old_content > div.choice_movie_box > div.choice_movie_info > table').find_all(
            'a'):  # 영화 기본정보
        p = re.compile(r'\d{2}.\d{2}')  # 가져온 정보가 날짜일때 ex) 05.04
        pa = re.compile(r'\d{4}')  # 가져온 정보가 년도일때 ex) 2022
        if pa.fullmatch(i.get_text()) is None:
            pass
        else:  # 가져온 정보가 년도라면 개봉 : 을 표시
            basicInfo += "\n개봉 : " + i.get_text() + "."
            continue

        if basicInfo.endswith("감독 : "):  # 문자열의 마지막이 감독 : 이라면, 뒤에 문자열을 이어붙히고 줄바꿈
            basicInfo += i.get_text() + "\n출연 : "
            continue

        if p.fullmatch(i.get_text()) is None:
            basicInfo += i.get_text() + " "
        else:  # 가져온 정보가 날짜라면 줄바꿈 후 감독 : 을 표시
            basicInfo += i.get_text() + "\n감독 : "

    rate = infoSoup.select_one('#old_content > div.choice_movie_box > div.choice_movie_info > table').find(
        'strong').get_text().replace("\n", "")

    try:  # 최신영화가 아니라 예매하기 버튼이 없는 경우 예외처리
        global reservationLink
        reservationLink = \
            infoSoup.select_one('#old_content > div.choice_movie_box > div.choice_movie_info > div.btn_area > a')[
                'href']  # 예매링크
        reservationLink = "https://movie.naver.com" + reservationLink
        lbl_movie_open["text"] = "현재 상영중 "
        btn_res["state"] = "normal"
    except Exception as ex:
        reservationLink = "https://movie.naver.com"  # 예매 못하는 경우면 네이버 영화 메인으로 이동되게
        lbl_movie_open["text"] = "상영 종료 "
        btn_res["state"] = "disabled"
        print(ex)

    lbl_movie_title['text'] = movieTitle
    lbl_movie_info['text'] = basicInfo
    lbl_movie_rate['text'] = rate

    posterImg = ImageTk.PhotoImage(Image.open("moviePoster.jpg"))
    lbl_picture['image'] = posterImg  # 영화 포스터 세팅


# 긍정/부정 키워드 세팅
def setReviewKeyword(movieName):
    if movieName in dicPositiveReview:
        positiveReview = dicPositiveReview[movieName]  # 딕셔너리에서 긍정 리뷰 키워드를 가져옴
        negativeReview = dicNegativeReview[movieName]
        positiveWordcloud = WordCloud(font_path=r"C:\Windows\Fonts\malgun.ttf", background_color='white',
                                      width=150,
                                      height=220, colormap='Greens').generate(positiveReview)
        negativeWordcloud = WordCloud(font_path=r"C:\Windows\Fonts\malgun.ttf", background_color='white',
                                      width=150,
                                      height=220, colormap='Reds').generate(negativeReview)
        positiveWordcloud.to_file(filename="positiveWordcloud.png")  # 이미지 저장(덮어쓰기)
        negativeWordcloud.to_file(filename="negativeWordcloud.png")

        positiveImage = tk.PhotoImage(file="positiveWordcloud.png")  # 저장한 이미지를 불러와 레이블에 삽입
        negativeImage = tk.PhotoImage(file="negativeWordcloud.png")
        lbl_positive['image'] = positiveImage
        lbl_negative['image'] = negativeImage

        posterImg = ImageTk.PhotoImage(Image.open("moviePoster.jpg"))
        lbl_picture['image'] = posterImg  # 영화 포스터 세팅
    else:
        lbl_positive['text'] = "리뷰가 부족합니다"
        lbl_negative['text'] = "리뷰가 부족합니다"

        posterImg = ImageTk.PhotoImage(Image.open("moviePoster.jpg"))
        lbl_picture['image'] = posterImg  # 영화 포스터 세팅

    posterImg = ImageTk.PhotoImage(Image.open("moviePoster.jpg"))
    lbl_picture['image'] = posterImg  # 영화 포스터 세팅


def reservationMovie():  # 예매링크로 이동
    webbrowser.open(reservationLink)


# 너무 긴 리뷰 자르기
def strSlicing(str):
    if len(str) > 60:
        return str[0:60] + "..."
    else:
        return str


# 학습 모델을 사용하여 분류
def predict_sentiment(model, sentence):
    sent = ko_tokenize(sentence)
    # print(sent)
    encoded = tok.texts_to_sequences([sent])
    # print(encoded)
    sample = keras.preprocessing.sequence.pad_sequences(encoded, maxlen=max_len)
    # print(sample)
    score = float(model.predict(sample))
    if score > 0.5:
        result = (1, score)
    else:
        result = (0, 1 - score)
    return result


# 긍정인지 부정인지 판단
def showPositive(int):
    if int == 1:
        return "긍정"
    else:
        return "부정"


# 학습 모델을 사용하여 분류한 리뷰의 평점을 예상하는 함수
def predict_sentiment_score(model, sentence):
    sent = ko_tokenize(sentence)
    encoded = tok.texts_to_sequences([sent])
    sample = keras.preprocessing.sequence.pad_sequences(encoded, maxlen=max_len)
    score = float(model.predict(sample))
    return int(str(score)[2:3]) + 1  # ex) score = 0.98342344 일때, 예상 평점 = 10점


# 실제 사용자가 매긴 평점 평균을 구하는 함수
def averageScore(MovieReviewList):
    sum = 0
    for i in range(len(MovieReviewList)):
        sum += int(MovieReviewList[i][1])
    return sum / len(MovieReviewList)


# 학습 모델을 사용하여 예측한 평점의 평균
def averageScore_predict(MovieReviewList):
    sum = 0
    for i in range(len(MovieReviewList)):
        sum += predict_sentiment_score(rnn_model, MovieReviewList[i][0])
    return sum / len(MovieReviewList)


def setMovieReviewList(MovieReviewList):
    txtListbox2.set(strSlicing(MovieReviewList[0][0]))
    lbl10['text'] = MovieReviewList[0][1] + '점'
    txtListbox3.set(strSlicing(MovieReviewList[1][0]))
    lbl13['text'] = MovieReviewList[1][1] + '점'
    txtListbox4.set(strSlicing(MovieReviewList[2][0]))
    lbl16['text'] = MovieReviewList[2][1] + '점'
    txtListbox5.set(strSlicing(MovieReviewList[3][0]))
    lbl19['text'] = MovieReviewList[3][1] + '점'
    txtListbox6.set(strSlicing(MovieReviewList[4][0]))
    lbl22['text'] = MovieReviewList[4][1] + '점'
    lbl8['text'] = str(predict_sentiment(rnn_model, MovieReviewList[0][0])[1])[2:4] + "% 확률로 " + showPositive(
        predict_sentiment(rnn_model, MovieReviewList[0][0])[0]) + "리뷰"
    lbl11['text'] = str(predict_sentiment(rnn_model, MovieReviewList[1][0])[1])[2:4] + "% 확률로 " + showPositive(
        predict_sentiment(rnn_model, MovieReviewList[1][0])[0]) + "리뷰"
    lbl14['text'] = str(predict_sentiment(rnn_model, MovieReviewList[2][0])[1])[2:4] + "% 확률로 " + showPositive(
        predict_sentiment(rnn_model, MovieReviewList[2][0])[0]) + "리뷰"
    lbl17['text'] = str(predict_sentiment(rnn_model, MovieReviewList[3][0])[1])[2:4] + "% 확률로 " + showPositive(
        predict_sentiment(rnn_model, MovieReviewList[3][0])[0]) + "리뷰"
    lbl20['text'] = str(predict_sentiment(rnn_model, MovieReviewList[4][0])[1])[2:4] + "% 확률로 " + showPositive(
        predict_sentiment(rnn_model, MovieReviewList[4][0])[0]) + "리뷰"
    lbl9['text'] = str(predict_sentiment_score(rnn_model, MovieReviewList[0][0])) + "점"
    lbl12['text'] = str(predict_sentiment_score(rnn_model, MovieReviewList[1][0])) + "점"
    lbl15['text'] = str(predict_sentiment_score(rnn_model, MovieReviewList[2][0])) + "점"
    lbl18['text'] = str(predict_sentiment_score(rnn_model, MovieReviewList[3][0])) + "점"
    lbl21['text'] = str(predict_sentiment_score(rnn_model, MovieReviewList[4][0])) + "점"
    txtListbox7.set(str(averageScore_predict(MovieReviewList))[0:3] + "점")  # n개의 리뷰 예상점수
    txtListbox8.set(str(averageScore(MovieReviewList))[0:3] + "점")  # 실제 사용자의 평균 점수
    lbl3['text'] = str(len(MovieReviewList)) + "개의 리뷰 예상 평균점수 : "
    lbl2['text'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " 기준 가장 최근 리뷰 5개"


# 초기화 버튼
def clear():
    txtListbox2.set("")
    lbl10['text'] = ""
    txtListbox3.set("")
    lbl13['text'] = ""
    txtListbox4.set("")
    lbl16['text'] = ""
    txtListbox5.set("")
    lbl19['text'] = ""
    txtListbox6.set("")
    lbl22['text'] = ""
    lbl8['text'] = ""
    lbl11['text'] = ""
    lbl14['text'] = ""
    lbl17['text'] = ""
    lbl20['text'] = ""
    lbl9['text'] = ""
    lbl12['text'] = ""
    lbl15['text'] = ""
    lbl18['text'] = ""
    lbl21['text'] = ""
    txtListbox7.set("")  # n개의 리뷰 예상점수
    txtListbox8.set("")  # 실제 사용자의 평균 점수
    lbl3['text'] = "n개의 리뷰 예상 평균점수 : "
    lbl2['text'] = "가장 최근 리뷰 5개"


txtListbox2 = tk.StringVar()  # 5개의 평점 listbox-1
txtListbox3 = tk.StringVar()  # 5개의 평점 listbox-2
txtListbox4 = tk.StringVar()  # 5개의 평점 listbox-3
txtListbox5 = tk.StringVar()  # 5개의 평점 listbox-4
txtListbox6 = tk.StringVar()  # 5개의 평점 listbox-5
txtListbox7 = tk.StringVar()  # 학습 100개의 리뷰평균 listbox
txtListbox8 = tk.StringVar()  # 실제 사용자의 점수평균 listbox
txtListbox9 = tk.StringVar()  # 영화 목록 listbox

# lbl_movie_title = tk.StringVar()  # 영화 제목
# lbl_movie_info = tk.StringVar()  # 영화 상세
# lbl_movie_rate = tk.StringVar()  # 영화 개봉 후 평점

# txtListbox13 = tk.StringVar()  # 영화 검색
txtListbox14 = tk.StringVar()  # 영화 검색 결과-1
txtListbox15 = tk.StringVar()  # 영화 검색 결과-2
txtListbox16 = tk.StringVar()  # 영화 검색 결과-3
txtListbox17 = tk.StringVar()  # 영화 검색 결과-4
txtListbox18 = tk.StringVar()  # 영화 검색 결과-5

'''2. 요소 생성'''
# 레이블
lbl1 = tk.Label(frm1, text='영화 선택')
lbl2 = tk.Label(frm1, text='가장 최근 리뷰 5개')
lbl3 = tk.Label(frm1, text='n개의 리뷰 예상 평균점수 : ')
lbl4 = tk.Label(frm1, text='실제 사용자의 평균점수 : ')
lbl5 = tk.Label(frm1, text='긍정/부정')
lbl6 = tk.Label(frm1, text='예상 평점')
lbl7 = tk.Label(frm1, text='실제 평점')

# 영화 사진
# lbl_picture = tk.Label(frm1, text='영화 사진')
# 영화 제목
lbl_title = tk.Label(frm7, text='영화 제목 : ')
lbl_info = tk.Label(frm7, text='영화 상세 : ')
lbl_rate = tk.Label(frm7, text='개봉후 평점 : ')
# 영화 검색
lbl_search = tk.Label(frm9, text='영화 검색')

# 긍정/부정 키워드
lbl_positive_text = tk.Label(frm1, text='긍정 리뷰 키워드')
lbl_negative_text = tk.Label(frm1, text='부정 리뷰 키워드')

# 리스트박스
listbox2 = tk.Label(frm1, width=50, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox2, wraplength=340)  # 5개의 평점 listbox-1
listbox3 = tk.Label(frm1, width=50, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox3, wraplength=340)  # 5개의 평점 listbox-2
listbox4 = tk.Label(frm1, width=50, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox4, wraplength=340)  # 5개의 평점 listbox-3
listbox5 = tk.Label(frm1, width=50, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox5, wraplength=340)  # 5개의 평점 listbox-4
listbox6 = tk.Label(frm1, width=50, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox6, wraplength=340)  # 5개의 평점 listbox-5
listbox7 = tk.Label(frm1, width=10, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox7)  # 학습 100개의 리뷰평균 listbox
listbox8 = tk.Label(frm1, width=10, borderwidth=2, relief="sunken", background="white", height=1,
                    textvariable=txtListbox8)  # 실제 사용자의 점수평균

scrollbar1 = tk.Scrollbar(frm3)  # 영화목록 리스트박스 스크롤 바
scrollbar1.pack(side="right", fill="y")

listbox9 = tk.Listbox(frm3, yscrollcommand=scrollbar1.set)  # 영화목록

# 영화제목 및 상세
lbl_movie_title = tk.Label(frm7, width=40, borderwidth=2, height=1, wraplength=340,
                           anchor='nw', justify='left', font=('맑은 고딕', 11, 'bold'))  # 영화 제목
lbl_movie_open = tk.Label(frm7, width=5, borderwidth=1, height=1,
                          anchor='ne', justify='left')  # 영화 개봉
lbl_movie_info = tk.Label(frm7, width=40, borderwidth=2, height=5, wraplength=340,
                          anchor='nw', justify='left')  # 영화 상세
lbl_movie_rate = tk.Label(frm7, width=10, borderwidth=2, height=1,
                          anchor='w', justify='left')  # 영화 개봉 후 평점

# 영화 검색
# listbox13 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=1,
# textvariable=txtListbox13, wraplength=340)  # 영화 검색
lbl_search = tk.Entry(frm9)  # 영화 검색
listbox14 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=2,
                     anchor='w', textvariable=txtListbox14, wraplength=340)  # 영화 검색 결과-1
listbox15 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=2,
                     anchor='w', textvariable=txtListbox15, wraplength=340)  # 영화 검색 결과-2
listbox16 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=2,
                     anchor='w', textvariable=txtListbox16, wraplength=340)  # 영화 검색 결과-3
listbox17 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=2,
                     anchor='w', textvariable=txtListbox17, wraplength=340)  # 영화 검색 결과-4
listbox18 = tk.Label(frm9, width=50, borderwidth=2, relief="sunken", background="white", height=2,
                     anchor='w', textvariable=txtListbox18, wraplength=340)  # 영화 검색 결과-5

# 영화 목록 리스트 삽입
listbox9.insert(0, "닥터 스트레인지: 대혼돈의 멀티버스")
listbox9.insert(1, "날씨의 아이")
listbox9.insert(2, "앵커")
listbox9.insert(3, "신비한 동물들과 덤블도어의 비밀")
listbox9.insert(4, "니 부모 얼굴이 보고 싶다")
listbox9.insert(5, "피아니스트의 전설")
listbox9.insert(6, "벤허")
listbox9.insert(7, "파수꾼")
listbox9.insert(8, "코다")
listbox9.insert(9, "와이키키 브라더스")
listbox9.insert(10, "피의 연대기")
listbox9.insert(11, "비긴 어게인")
listbox9.insert(12, "개를 훔치는 완벽한 방법")
listbox9.insert(13, "중경삼림")
listbox9.insert(14, "찬실이는 복도 많지")
listbox9.insert(15, "바닷마을 다이어리")
listbox9.insert(16, "귀향")
listbox9.insert(17, "세자매")
listbox9.insert(18, "안경")
listbox9.insert(19, "라라랜드")
listbox9.insert(20, "공기살인")
listbox9.insert(21, "범죄도시2")
listbox9.insert(22, "쥬라기월드: 도미니언")
listbox9.insert(23, "그대가 조국")

listbox9.pack(side="left", fill="y")  # 영화 목록 listbox

scrollbar1["command"] = listbox9.yview

lbl8 = tk.Label(frm1, width=20, height=2, borderwidth=2, relief="sunken", background="white")  # 긍정/부정-1
lbl9 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 학습데이터가 판단한 예상 평점-1
lbl10 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 실제 사용자가 남긴 평점-1
lbl11 = tk.Label(frm1, width=20, height=2, borderwidth=2, relief="sunken", background="white")  # 긍정/부정-2
lbl12 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 학습데이터가 판단한 예상 평점-2
lbl13 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 실제 사용자가 남긴 평점-2
lbl14 = tk.Label(frm1, width=20, height=2, borderwidth=2, relief="sunken", background="white")  # 긍정/부정-3
lbl15 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 학습데이터가 판단한 예상 평점-3
lbl16 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 실제 사용자가 남긴 평점-3
lbl17 = tk.Label(frm1, width=20, height=2, borderwidth=2, relief="sunken", background="white")  # 긍정/부정-4
lbl18 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 학습데이터가 판단한 예상 평점-4
lbl19 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 실제 사용자가 남긴 평점-4
lbl20 = tk.Label(frm1, width=20, height=2, borderwidth=2, relief="sunken", background="white")  # 긍정/부정-5
lbl21 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 학습데이터가 판단한 예상 평점-5
lbl22 = tk.Label(frm1, width=10, height=2, borderwidth=2, relief="sunken", background="white")  # 실제 사용자가 남긴 평점-5

# 긍정/부정 키워드
lbl_positive = tk.Label(frm1, relief="sunken", background="white")  # 긍정 키워드
lbl_negative = tk.Label(frm1, relief="sunken", background="white")  # 부정 키워드

# 영화 사진
lbl_picture = tk.Label(frm5)  # 영화 사진

# 버튼
btn1 = tk.Button(frm4, text="검색", width=10, command=lambda: searchMovieReview("0"))  # 영화 선택 버튼
btn0 = tk.Button(frm2, text="초기화", width=8, command=clear)  # 초기화 버튼
btn_res = tk.Button(frm7, text="예매하기", width=8, state="disabled",
                    command=reservationMovie)  # command=reservationMovie)  # 예매하기 버튼
btn_search = tk.Button(frm9, text="검색", width=8, command=searchMovie)  # 영화 선택 버튼

btn_search1 = tk.Button(frm9, text="선택", width=5, command=lambda: searchMovieReview(searchedMovie[0][1]))  # 영화 선택 -1
btn_search2 = tk.Button(frm9, text="선택", width=5, command=lambda: searchMovieReview(searchedMovie[1][1]))  # 영화 선택 -2
btn_search3 = tk.Button(frm9, text="선택", width=5, command=lambda: searchMovieReview(searchedMovie[2][1]))  # 영화 선택 -3
btn_search4 = tk.Button(frm9, text="선택", width=5, command=lambda: searchMovieReview(searchedMovie[3][1]))  # 영화 선택 -4
btn_search5 = tk.Button(frm9, text="선택", width=5, command=lambda: searchMovieReview(searchedMovie[4][1]))  # 영화 선택 -5

'''3. 요소 배치'''
# 영화 사진
lbl_picture.grid(row=1, column=0, columnspan=9, sticky="we")  # 영화 사진

# 상단 프레임
lbl2.grid(row=1, column=0, columnspan=9, sticky="we")  # 5개의 평점 레이블
lbl3.grid(row=7, column=0, columnspan=3, sticky="ne")  # 학습 100개의 리뷰평균 레이블
lbl4.grid(row=8, column=0, columnspan=3, sticky="ne")  # 실제 사용자의 점수평균 레이블
lbl5.grid(row=1, column=10, sticky="n")  # 긍정/부정
lbl6.grid(row=1, column=11, sticky="n")  # 학습데이터가 판단한 예상 평점
lbl7.grid(row=1, column=12, sticky="n")  # 실제 사용자가 남긴 평점

# 긍정/부정 키워드
lbl_positive_text.grid(row=1, column=13, sticky="n")  # 긍정
lbl_negative_text.grid(row=1, column=14, sticky="n")  # 부정

lbl_title.grid(row=1, column=0, columnspan=3, sticky="w")  # 영화 제목
lbl_info.grid(row=2, column=0, columnspan=3, sticky="nw")  # 영화 상세
lbl_rate.grid(row=3, column=0, columnspan=3, sticky="ne")  # 영화 개봉 후 평점

lbl_search.grid(row=1, column=0, columnspan=7)  # 영화 검색

# 긍정/부정, 평점부분
lbl8.grid(row=2, column=10, rowspan=1, sticky="n", pady=5)  # 긍정/부정-1
lbl9.grid(row=2, column=11, rowspan=1, sticky="n", pady=5)  # 학습데이터가 판단한 예상 평점-1
lbl10.grid(row=2, column=12, rowspan=1, sticky="n", pady=5)  # 실제 사용자가 남긴 평점-1
lbl11.grid(row=3, column=10, rowspan=1, sticky="n", pady=5)  # 긍정/부정-2
lbl12.grid(row=3, column=11, rowspan=1, sticky="n", pady=5)  # 학습데이터가 판단한 예상 평점-2
lbl13.grid(row=3, column=12, rowspan=1, sticky="n", pady=5)  # 실제 사용자가 남긴 평점-2
lbl14.grid(row=4, column=10, rowspan=1, sticky="n", pady=5)  # 긍정/부정-3
lbl15.grid(row=4, column=11, rowspan=1, sticky="n", pady=5)  # 학습데이터가 판단한 예상 평점-3
lbl16.grid(row=4, column=12, rowspan=1, sticky="n", pady=5)  # 실제 사용자가 남긴 평점-3
lbl17.grid(row=5, column=10, rowspan=1, sticky="n", pady=5)  # 긍정/부정-4
lbl18.grid(row=5, column=11, rowspan=1, sticky="n", pady=5)  # 학습데이터가 판단한 예상 평점-4
lbl19.grid(row=5, column=12, rowspan=1, sticky="n", pady=5)  # 실제 사용자가 남긴 평점-4
lbl20.grid(row=6, column=10, rowspan=1, sticky="n", pady=5)  # 긍정/부정-5
lbl21.grid(row=6, column=11, rowspan=1, sticky="n", pady=5)  # 학습데이터가 판단한 예상 평점-5
lbl22.grid(row=6, column=12, rowspan=1, sticky="n", pady=5)  # 실제 사용자가 남긴 평점-5

listbox2.grid(row=2, column=0, columnspan=9, sticky="wens", pady=5)  # 5개의 평점 listbox-1
listbox3.grid(row=3, column=0, columnspan=9, sticky="wens", pady=5)  # 5개의 평점 listbox-2
listbox4.grid(row=4, column=0, columnspan=9, sticky="wens", pady=5)  # 5개의 평점 listbox-3
listbox5.grid(row=5, column=0, columnspan=9, sticky="wens", pady=5)  # 5개의 평점 listbox-4
listbox6.grid(row=6, column=0, columnspan=9, sticky="wens", pady=5)  # 5개의 평점 listbox-5
listbox7.grid(row=7, column=3, columnspan=2, sticky="wens")  # 학습 100개의 리뷰평균 listbox
listbox8.grid(row=8, column=3, columnspan=2, sticky="wens")  # 실제 사용자의 점수평균 listbox

# 긍정/부정 키워드
lbl_positive.grid(row=2, column=13, rowspan=5, sticky=tk.W + tk.E + tk.N + tk.S)  # 긍정 키워드
lbl_negative.grid(row=2, column=14, rowspan=5, sticky=tk.W + tk.E + tk.N + tk.S)  # 부정 키워드

# 영화 정보
lbl_movie_title.grid(row=1, column=3, columnspan=6, sticky="wens", pady=5)  # 영화 제목
lbl_movie_open.grid(row=1, column=8, rowspan=1, sticky="wens", pady=5)  # 영화 개봉
lbl_movie_info.grid(row=2, column=3, columnspan=9, sticky="wens", pady=5)  # 영화 상세
lbl_movie_rate.grid(row=3, column=3, columnspan=2, sticky="wens")  # 영화 개봉 후 평점

# 영화 검색
# listbox13.grid(row=1, column=3, columnspan=6, sticky="wns", pady=5)  # 영화 검색
listbox14.grid(row=2, column=3, columnspan=9, sticky="wns", pady=5)  # 영화 검색 결과-1
listbox15.grid(row=3, column=3, columnspan=9, sticky="wns", pady=5)  # 영화 검색 결과-2
listbox16.grid(row=4, column=3, columnspan=9, sticky="wens", pady=5)  # 영화 검색 결과-3
listbox17.grid(row=5, column=3, columnspan=9, sticky="wens", pady=5)  # 영화 검색 결과-4
listbox18.grid(row=6, column=3, columnspan=9, sticky="wens", pady=5)  # 영화 검색 결과-5

# 버튼
btn1.grid(row=0, column=0, sticky="n")  # 영화 선택 버튼
btn_res.grid(row=1, column=9, sticky="n")  # 영화 예매 버튼
btn_search.grid(row=1, column=9, sticky="n")  # 영화 검색 버튼

btn_search1.grid(row=2, column=13, sticky="we")  # 영화 검색 버튼-1
btn_search2.grid(row=3, column=13, sticky="we")  # 영화 검색 버튼-2
btn_search3.grid(row=4, column=13, sticky="we")  # 영화 검색 버튼-3
btn_search4.grid(row=5, column=13, sticky="we")  # 영화 검색 버튼-4
btn_search5.grid(row=6, column=13, sticky="we")  # 영화 검색 버튼-5

# 하단 프레임
btn0.grid(row=0, column=0)

'''실행'''
root.mainloop()
