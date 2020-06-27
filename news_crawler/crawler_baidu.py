import random
import re
import urllib.parse
import urllib.request


class BaiDuNewsCrawler(object):
    """
    百度新闻爬虫
    """
    # 请求头地址
    __ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    ]

    def __init__(self, key_word):
        self.key_word = key_word

    def get_headers(self):
        """
        设置headrs内容
        :return:
        """
        headers = {
            'Host': 'www.baidu.com',
        }
        ua = random.choice(self.__ua_list)
        headers.update({"User-Agent": ua})
        return headers

    def __set_query_string_parameters(self, page):
        """
        设置查询参数
        :return:
        """
        url_query_parse = {

            "tn": "newstitledy",
            "word": self.key_word,
            "pn": (page-1) * 20,
            "rn": 20,
            "ie": 'utf-8',
            'bt': 0,
            'et': 0,
            'cl': 2,
            'ct': 0,
        }
        url_query_parse = urllib.parse.urlencode(url_query_parse)
        return url_query_parse

    def get_url(self, page):
        """
        构造url链接
        :param page:
        :return:
        """
        url_query_parse = self.__set_query_string_parameters(page)
        url = 'https://news.baidu.com/ns?{}'.format(url_query_parse)
        return url

    def start(self):
        """
        开始抓取
        :return:
        """
        headers = self.get_headers()
        url = self.get_url(1)
        print(url)
        req = urllib.request.Request(url=url, headers=headers, method='GET')
        txt = urllib.request.urlopen(req).read().decode('utf-8')
        txt = re.sub(r"\s{2,}", ' ', txt)
        print(txt)


if __name__ == '__main__':
    news = BaiDuNewsCrawler("上海大学")

    news.start()
