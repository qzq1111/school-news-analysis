"""
用于html解析
"""

import re


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

    def parse_new(self):
        """
        解析出新闻数据
        :return:
        """

        for new in self.news_list:
            # 解析链接
            new_link = re.search(r'<a\s*href="(\S+)"\s*data-click', new, re.I)
            print(new_link.group(1))
            # 解析标题
            new_title = re.search(r'target="_blank">([\d\D]*)(</a>\s*</h3>)', new, re.I)
            print(new_title.group(1))
            # 解析发布者及时间
            author_time = re.search(
                r'<div class="c-title-author">(\S+)&nbsp;&nbsp;((\d+分钟前)|(\d+小时前)|(\d+年\d+月\d+日 \d+:\d+))', new, re.I)
            print(author_time.group(1))
            print(author_time.group(2))
            # 解析查询更多相同新闻
            more_link = re.search(r'<a\s*href="(\S+)"\s*class="c-more_link"', new, re.I)
            if more_link:
                print(more_link.group(1))

    @property
    def data(self):
        return self._data


if __name__ == '__main__':
    with open('examples_html/clean.html', 'r', encoding='utf-8') as f:
        data = f.read()
        data_parse = HtmlParse(data)
        data_parse.parse_news_list()
        data_parse.parse_new()
