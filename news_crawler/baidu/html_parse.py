"""
用于html解析
"""

import re
from datetime import datetime, timedelta


class HtmlParse(object):

    def __init__(self, html_string: str, key: str):
        """

        :param html_string:html字符串
        :param key: 关键字
        """
        self._data = html_string
        self.key = key
        self.__clean()

    def __clean(self):
        """
        数据清洗，删除html script/style
        :return:
        """
        # 删除script
        self._data = re.sub(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', '', self._data, flags=re.I)
        # 删除style
        self._data = re.sub(r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', '', self._data, flags=re.I)
        # 删除多余的空格及换行符
        self._data = re.sub(r'\s{2,}', '', self._data)
        # 删除无法删除的script
        while self._data.find('<script>') != -1:
            start_index = self._data.find('<script>')
            end_index = self._data.find('</script>')
            if end_index == -1:
                break
            self._data = self._data[:start_index] + self._data[end_index + len('</script>'):]
        # 处理多余的titlelast
        self._data = re.sub(r'\s*?titlelast', '', self._data, flags=re.I)

    @staticmethod
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
                return now.strftime('%Y年%m月%d日 %H:%M')

            elif '小时前' in time_string:
                hour = re.search(r'\d+', time_string)
                if hour:
                    hour = hour.group()
                    now = datetime.now() - timedelta(hours=int(hour))
                else:
                    now = datetime.now()
                return now.strftime('%Y年%m月%d日 %H:%M')
            else:
                return time_string

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
        news_list = []
        while wait_parse_string.find('<div class="result title"') != -1:

            start_index = wait_parse_string.find(flag)
            end_index = wait_parse_string[start_index + flag_length:].find(flag)
            if end_index > 0:
                end_index = start_index + end_index + flag_length
            else:
                end_index = len(wait_parse_string)
            news_list.append(wait_parse_string[start_index:end_index])
            wait_parse_string = wait_parse_string[end_index:]
        return news_list

    def parse_news(self, news_list):
        """
        解析出新闻数据
        :return:
        """

        news_data = []
        for news in news_list:
            temp = {
                "news_key": self.key,
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
                temp["news_time"] = self.time_convert(author_time.group(2))
            # 解析查询更多相同新闻
            more_link = re.search(r'<a\s*href="(\S+)"\s*class="c-more_link"', news, re.I)
            if more_link:
                temp["more_link"] = more_link.group(1)

            news_data.append(temp)

        return news_data

    def start(self):
        """
        清洗并返回新闻数据
        :return:
        """
        news_list = self.parse_news_list()
        news = self.parse_news(news_list)
        return news


if __name__ == '__main__':
    with open('examples_html/original.html', 'r', encoding='utf-8') as f:
        data = f.read()
        data_parse = HtmlParse(data, '北京大学')
        print(data_parse.start())
