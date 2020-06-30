"""
用于html解析
"""

import re
from datetime import datetime, timedelta


def time_convert(time_string: str):
    """
    标准化日期字符串
    :param time_string:
    :return:
    """
    if not time_string:
        return ''
    else:
        if '分钟前' in time_string:
            minute = re.search(r'\d+', time_string)
            if minute:
                minute = minute.group()
                now = datetime.now() - timedelta(minutes=int(minute))
            else:
                now = datetime.now()
            return now.strftime('%Y年%m月%d日 %H:%M:%S')

        elif '小时前' in time_string:
            hour = re.search(r'\d+', time_string)
            if hour:
                hour = hour.group()
                now = datetime.now() - timedelta(hours=int(hour))
            else:
                now = datetime.now()
            return now.strftime('%Y年%m月%d日 %H:%M:%S')
        else:
            return time_string


class HtmlParse(object):

    def __init__(self, html_string: str):
        self._data = html_string
        self.news_list = []

    def parse_news_list(self):
        """
        分割解析出单条新闻字符串
        :return:
        """
        # 取出解析的数据字符串
        wait_parse_string = re.search(r'<div id="content_left">([\s\S]*)<div id="gotoPage">', self._data)

        if not wait_parse_string:
            return
        wait_parse_string = wait_parse_string.group()
        # 移除最后多余字符串
        wait_parse_string = re.sub(r'</div></div><div id="gotoPage">', '', wait_parse_string)

        flag = '<div class="result title"'
        flag_length = len(flag)
        # 遍历字符串并分割出单条新闻数据
        while wait_parse_string.find('<div class="result title"') != -1:

            start_index = wait_parse_string.find(flag)
            end_index = wait_parse_string[start_index + flag_length:].find(flag)
            if end_index > 0:
                end_index = start_index + end_index + flag_length
            else:
                end_index = len(wait_parse_string)
            self.news_list.append(wait_parse_string[start_index:end_index])
            wait_parse_string = wait_parse_string[end_index:]

    def parse_news(self):
        """
        解析出新闻数据
        :return:
        """

        news_data = []
        for news in self.news_list:
            temp = {
                "news_title": '',
                'news_link': '',
                'news_author': '',
                'news_time': '',
                'more_link': '',
            }

            # 解析链接
            news_link = re.search(r'<a\s*href="(\S+)"\s*data-click', news, re.I)
            if news_link:
                temp["news_link"] = news_link.group(1)
            # 解析标题
            news_title = re.search(r'target="_blank">([\d\D]*)(</a>\s*</h3>)', news, re.I)
            if news_title:
                temp["news_title"] = news_title.group(1)
            # 解析发布者及时间
            author_time = re.search(
                r'<div class="c-title-author">(\S+)&nbsp;&nbsp;((\d+分钟前)|(\d+小时前)|(\d+年\d+月\d+日 \d+:\d+))', news, re.I)
            if author_time:
                temp["news_author"] = author_time.group(1)
                temp["news_time"] = time_convert(author_time.group(2))
            # 解析查询更多相同新闻
            more_link = re.search(r'<a\s*href="(\S+)"\s*class="c-more_link"', news, re.I)
            if more_link:
                temp["more_link"] = more_link.group(1)

            news_data.append(temp)

        return news_data

    @property
    def data(self):
        return self._data


if __name__ == '__main__':
    with open('examples_html/clean.html', 'r', encoding='utf-8') as f:
        data = f.read()
        data_parse = HtmlParse(data)
        data_parse.parse_news_list()
        print(data_parse.parse_news())
