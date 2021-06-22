import json
import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import pandas_datareader as pdr
import datetime
import matplotlib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import cufflinks as cf
from rest_framework.response import Response

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rest_framework.views import APIView


def stock(request):
    return render(request, 'stock/kospi.html')


def jenkins_test(request):
    return render(request, 'stock/jenkinsTest.html')


class stock_detail(APIView):
    def get(self, request, **kwargs):
        # https://chancoding.tistory.com/116?category=846070
        # #start를 위해 가져올 날짜 설정
        date = request.GET.get('date')
        print(date)

        stock_code = request.GET.get('stock_code') + '.KS'
        print(stock_code)

        stock_name = request.GET.get('stock_name')
        print(stock_name)

        cur_year = datetime.datetime.now().year
        cur_month = datetime.datetime.now().month
        cur_day = datetime.datetime.now().day

        start = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:]))

        end = datetime.datetime(cur_year, cur_month, cur_day)

        # 야후에서 삼성전자 데이터 가져오기
        stock = pdr.get_data_yahoo(stock_code, start, end)

        # plot = stock.iplot(asFigure=True, title=stock_name, xTitle='날짜', yTitle='거래량')
        plot = stock.iplot(asFigure=True, title=stock_name, xTitle='date', yTitle='volume')

        print(plot)
        plot.to_json()
        print('plot json 는 ' + plot.to_json())
        stock_dict = {'stockGraph': plot.to_json()}
        return JsonResponse(stock_dict, json_dumps_params={'ensure_ascii': False})


class stock_information(APIView):
    def get(self, request, **kwargs):
        # 크롤링을 해서 가져오는 경우
        stock_dict = {}
        query = request.GET.get('query')
        print(query)
        url = 'http://www.sedaily.com/Stock/Quote?type=' + query
        try:
            html = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            soup = BeautifulSoup(html.text, 'lxml')

        all_table = soup.find_all('div', {'class': 'table'})

        for thead in all_table:
            dl = thead.find('dl', {'class': 'thead'})
            dt = dl.find('dt')
            fieldName = dt.text
            # print(fieldName)
            # print(dt)
            tbody = thead.find_all('dl', {'class', 'tbody'})

            count = 0

            for dl in tbody:
                name = dl.find('dt').get_text()
                # print(name)
                dd = dl.find('dd')
                price = tbody[count].find('span').get_text().replace(',', '')
                # print(price)
                code = dd.get('id').replace('dd_Item_', '')

                # print(code)
                stock_dict[code] = [name, fieldName, price]
                count += 1

        # data = json.dumps(stock_dict)

        # sorting test
        # sorted_dict = sorted(stock_dict.items())
        # sorted_dict.sort(key=lambda x: x[1][1])
        # # print(sorted_dict)
        # stock_dict = dict(sorted_dict)
        # print(stock_dict)

        # 한글이 유니코드로 출력되지 않도록 json_dumps_params 설정
        # return JsonResponse(stock_dict, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(stock_dict, json_dumps_params={'ensure_ascii': False})


class stock_graph(APIView):
    def get(self, request, **kwargs):
        date = request.GET.get('date')
        print(type(date))
        print(date)

        cur_year = datetime.datetime.now().year
        # print(type(cur_year)) #int
        cur_month = datetime.datetime.now().month
        cur_day = datetime.datetime.now().day

        pd.set_option('precision', 4)

        start = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:]))
        end = datetime.datetime(cur_year, cur_month, cur_day)
        # start = datetime.datetime(2021, 5, 1)
        # end = datetime.datetime(2021, 5, 14)
        df_null = pdr.DataReader("^KS11", "yahoo", start, end)
        df = df_null.dropna()

        kospi_chart = df.Close.plot(style='b')
        kospi_chart.set_title("KOSPI")
        # kospi_chart.set_ylabel("kospi")
        kospi_chart.set_xlabel("date")
        kospi_chart.set_xlim(str(start), str(end))

        # print(df)

        # print("Close Median", df['Close'].median())
        # print(df['Close'].describe())
        # print(df.corr())

        # plt.show()
        plt.savefig("./stock/static/img/kospi.png")
        img_url = '/stock/static/img/kospi.png'
        data = json.dumps({'date': date, 'img_url': img_url})

        # return render(request, 'stock/test.html', {'date': date, 'img_url': img_url})
        # return HttpResponse({'date': date, 'img_url': img_url})

        return HttpResponse(data)
