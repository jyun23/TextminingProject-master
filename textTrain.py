import pandas as pd
from konlpy.tag import Okt
from keras.preprocessing.text import Tokenizer
from tokenized_text import train_text_import

train_data = pd.read_table('naver_movie_ratings_train.txt')  # 15만개

# 중복 제거: document 칼럼의 값만을 기준으로 중복 여부 판정, 별도의 객체 생성하지 않고 기존 객체에 덮어씀.
train_data.drop_duplicates(subset=['document'], inplace=True)

# 널 값을 가진 샘플 삭제
train_data = train_data.dropna(how='any')  # 널 값이 하나라도 존재하는 행 제거

tagger = Okt()

train_text = train_text_import

tok = Tokenizer()
tok.fit_on_texts(train_text)
max_len = 30

# 출현 빈도(1~5)별 단어 개수 확인
counts = [len(tok.word_index), 0, 0, 0, 0, 0]
for key, freq in tok.word_counts.items():
    if freq <= 5:
        counts[freq] = counts[freq] + 1
counts

count2 = counts[0] - counts[1]
print(f'2회 이상 출현한 단어 개수: {count2}')
count3 = count2 - counts[2]
print(f'3회 이상 출현한 단어 개수: {count3}')

# 학습 데이터 각 토큰에 정수 인덱스 할당, 빈도 카운트
# 빈도 기준 상위 vocab_size 개수(3회 이상 출현한 단어 개수)만 단어 유지
# OOV 토큰을 하나 추가
vocab_size = count3 + 1
tok = Tokenizer(vocab_size, oov_token='OOV')
tok.fit_on_texts(train_text)
