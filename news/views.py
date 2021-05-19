# 파이썬 크롤링 출처
# https://everyday-tech.tistory.com/entry/%EC%89%BD%EA%B2%8C-%EB%94%B0%EB%9D%BC%ED%95%98%EB%8A%94-%EB%84%A4%EC%9D%B4%EB%B2%84-%EB%89%B4%EC%8A%A4-%ED%81%AC%EB%A1%A4%EB%A7%81python-2%ED%83%84
import requests
from bs4 import BeautifulSoup
import re

from rest_framework import response
from rest_framework.response import Response

from . import serializer
from .models import News
from .serializer import NewsSerializer


def news_list(request):
    if request.method == 'GET':
        query = input('검색 키워드를 입력하세요 : ')  # 도도코인
        news_num = int(input('총 필요한 뉴스기사 수를 입력해주세요(숫자만 입력) : '))
        query = query.replace(' ', '+')  # '도도코인 +'

        news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'

        req = requests.get(news_url.format(query))
        print(news_url)
        soup = BeautifulSoup(req.text, 'html.parser')

        news_dict = {}
        idx = 0
        cur_page = 1

        print()
        print('크롤링 중...')

        while idx < news_num:
            ### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###

            table = soup.find('ul', {'class': 'list_news'})
            li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
            area_list = [li.find('div', {'class': 'news_area'}) for li in li_list]
            a_list = [area.find('a', {'class': 'news_tit'}) for area in area_list]

            for n in a_list[:min(len(a_list), news_num - idx)]:
                # news_dict[idx] = {'title': n.get('title'),
                #                   'url': n.get('href')}
                # idx += 1

                news_dict[n.get('title')] = n.get('href')
                idx += 1

            cur_page += 1

            pages = soup.find('div', {'class': 'sc_page_inner'})
            next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')

            req = requests.get('https://search.naver.com/search.naver' + next_page_url)
            soup = BeautifulSoup(req.text, 'html.parser')

        print('크롤링 완료')
        print(news_dict)
    return Response()
