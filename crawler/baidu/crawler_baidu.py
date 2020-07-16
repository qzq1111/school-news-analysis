import random
import re
import time
import urllib.parse
import urllib.request

from crawler.baidu.html_parse import HtmlParse
from utils.logger import logger
from utils.mongo_utils import MongoDB


class BaiDuNewsCrawler(object):
    """
    百度新闻爬虫
    """
    # 请求头地址
    __ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    ]

    html_parse = HtmlParse

    def __init__(self, key_word, start_page=1, stop_page=-1):
        """
        :param key_word: 抓取的关键字
        :param start_page: 起始页
        :param stop_page: 停止抓取的页数，如果为-1,则抓取全部数据
        """
        self.key_word = key_word
        if stop_page != -1 and start_page > stop_page:
            raise ValueError('开始页不能大于停止页')
        self.start_page = start_page
        self.stop_page = stop_page
        # 当前页
        self.__current_page = start_page
        # 连接mongodb
        self.mongo = MongoDB()

    def get_headers(self):
        """
        设置headrs内容
        :return:
        """
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'Host': 'news.baidu.com',

        }
        ua = random.choice(self.__ua_list)
        headers.update({"User-Agent": ua})
        return headers

    def __set_query_string_parameters(self):
        """
        设置查询参数
        :return:
        """
        url_query_parse = {
            "tn": "newstitle",
            "word": "title:({})".format(self.key_word),
            "pn": (self.__current_page - 1) * 20,
            "rn": 20,
            "ie": 'utf-8',
            'bt': 0,
            'et': 0,
            'cl': 2,
            'ct': 0,
        }
        url_query_parse = urllib.parse.urlencode(url_query_parse)
        return url_query_parse

    def get_url(self):
        """
        构造url链接
        :param page:
        :return:
        """
        url_query_parse = self.__set_query_string_parameters()
        url = 'https://news.baidu.com/ns?{}'.format(url_query_parse)
        return url

    def __check_stop_page(self):
        """
        判断是否设置停止抓取的页数
        :return:
        """
        if self.stop_page == -1:
            return False
        elif self.stop_page > self.__current_page:
            return False
        else:
            return True

    @staticmethod
    def __check_next_page(page_data):
        """
        判断是否还有下一页
        :return:
        """
        next_page = re.search(r'<a\s+href="(\S+)"\s+class="n">下一页&gt;</a>', page_data)
        if next_page:
            return True
        else:
            return False

    def start(self):
        """
        开始抓取
        :return:
        """
        headers = self.get_headers()

        while 1:
            url = self.get_url()
            try:
                logger.info('开始抓取第{}页.....'.format(self.__current_page))
                logger.info('抓取地址:{}'.format(url))
                req = urllib.request.Request(url=url, headers=headers, method='GET')
                html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
                # TODO:暂时不分离处理数据，处理之后写入mongodb
                logger.info('第{}页数据处理中.....'.format(self.__current_page))
                parse = self.html_parse(html_string=html, key=self.key_word)
                self.mongo.write_news(parse.start())
                # 判断是否为停止页，或者是否全部抓取完成
                if self.__check_stop_page() or not self.__check_next_page(html):
                    logger.info('数据全部抓取完成，共抓取{}页'.format(self.__current_page))
                    break
            except Exception as e:
                logger.error('第{}页抓取失败...'.format(self.__current_page))
                logger.exception(e)
            # 更新当前页
            self.__current_page += 1
            time.sleep(2)
        self.mongo.conn.close()


if __name__ == '__main__':
    news = BaiDuNewsCrawler("北京大学", start_page=1, stop_page=10)
    news.start()
