import logging
import random
import re
import time
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class BaiDuNewsCrawler(object):
    """
    百度新闻爬虫
    """
    # 请求头地址
    __ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    ]

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

    def check_stop_page(self):
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

    def check_next_page(self, page_data):
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
            logger.info(url)
            try:
                logger.info('开始抓取第{}页.....'.format(self.__current_page))
                req = urllib.request.Request(url=url, headers=headers, method='GET')
                html = urllib.request.urlopen(req).read().decode('utf-8')
                # TODO:存储
                # 判断是否为停止页，或者是否全部抓取完成
                if self.check_stop_page() or not self.check_next_page(html):
                    logger.info('数据全部抓取完成，共抓取{}页'.format(self.__current_page))
                    break
            except Exception as e:
                logger.error('第{}页抓取失败...'.format(self.__current_page))
                logger.exception(e)
            # 更新当前页
            self.__current_page += 1
            time.sleep(2)


if __name__ == '__main__':
    news = BaiDuNewsCrawler("北京大学", start_page=1, stop_page=5)
    news.start()
