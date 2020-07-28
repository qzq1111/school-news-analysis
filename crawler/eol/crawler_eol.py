import json
import random
import urllib.parse
import urllib.request

from utils.logger import logger
from utils.mongo_utils import MongoDB


class CrawlerEol(object):
    """
    中国高校基本信息抓取
    """
    # 请求头地址
    __ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
    ]

    def __init__(self, key_word=None):
        """

        :param key_word: 学校关键字
        """
        # 连接mongodb
        self.mongo = MongoDB()
        self.key_word = key_word
        self.school_code = None

    def set_headers(self, headers):
        """
        设置headrs内容
        :return:
        """
        ua = random.choice(self.__ua_list)
        headers.update({"User-Agent": ua})
        return headers

    def search_school(self):
        """
        搜索学校信息
        :return:
        """
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Cookie': 'areaid=44; cityid=4401',
            'Host': 'api.eol.cn',
            'Origin': 'https://gkcx.eol.cn',
        }
        headers = self.set_headers(headers)
        param = {
            'access_token': '',
            'keyword': self.key_word,
            'page': 1,
            'signsafe': '',
            'size': 20,
            'sort': 'view_total',
            'uri': 'apidata/api/gk/school/lists',

        }
        url_query_parse = urllib.parse.urlencode(param)
        url = 'https://api.eol.cn/gkcx/api/?{}'.format(url_query_parse)
        logger.info('{}:搜索列表中....'.format(self.key_word))
        try:
            req = urllib.request.Request(url=url, headers=headers, method='GET')
            json_data = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            json_data = json.loads(json_data)
        except Exception as e:
            logger.error('{}:搜索失败!!'.format(self.key_word))
            logger.exception(e)
            json_data = None

        return json_data

    def get_school_info(self):
        """
        获取学校信息
        :return:
        """
        if self.school_code is None:
            raise ValueError('学校代码错误')
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://gkcx.eol.cn/school/{}'.format(self.school_code),
        }
        headers = self.set_headers(headers)
        url = 'https://static-data.eol.cn/www/2.0/school/{}/info.json'.format(self.school_code)
        logger.info('{}:获取基本信息中....'.format(self.key_word))
        try:
            req = urllib.request.Request(url=url, headers=headers, method='GET')
            json_data = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            json_data = json.loads(json_data)
        except Exception as e:
            logger.error('{}:获取基本信息失败!!'.format(self.key_word))
            logger.exception(e)
            json_data = None

        return json_data

    def get_school_detail(self):
        """
        获取学校简介
        :return:
        """
        if self.school_code is None:
            raise ValueError('学校代码错误')
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Host': 'static-data.eol.cn',
            'Origin': 'https://gkcx.eol.cn',
            'Referer': 'https://gkcx.eol.cn/school/{}/introDetails'.format(self.school_code)
        }
        headers = self.set_headers(headers)
        url = 'https://static-data.eol.cn/www/school/{}/detail/69000.json'.format(self.school_code)
        logger.info('{}:获取学校简介中....'.format(self.key_word))
        try:
            req = urllib.request.Request(url=url, headers=headers, method='GET')
            json_data = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            json_data = json.loads(json_data)
        except Exception as e:
            logger.error('{}:获取简介失败!!'.format(self.key_word))
            logger.exception(e)
            json_data = dict()

        return json_data

    def start(self):
        """
        数据下载
        :return:
        """
        # 第一步：搜索获取学校code
        search_list = self.search_school()
        # 无法搜索到数据
        if not search_list:
            return
        # 获取搜索结果数据
        search_data = search_list.get('data')
        item = search_data.get('item')
        if not item:
            return
        item = item[0]
        self.school_code = item.get("school_id")
        # 获取学校基本信息
        school_info = self.get_school_info()
        if not school_info:
            return

        # 获取结果数据
        school_info = school_info.get('data')

        # 获取学校简介详情
        school_detail = self.get_school_detail()

        data = dict(
            school_code=self.school_code,
            # 学校名字
            name=item.get("name"),
            # 当月浏览量
            view_month=item.get("view_month"),
            # 总浏览量
            view_total=item.get("view_total"),
            view_total_number=item.get("view_total_number"),
            # 周浏览量
            view_week=item.get("view_week"),
            # 学校旧的名称
            old_name=school_info.get("old_name"),
            province_name=school_info.get("province_name"),
            city_name=school_info.get("city_name"),
            town_name=school_info.get("town_name"),
            belong=school_info.get("belong"),
            f985=school_info.get("f985"),
            f211=school_info.get("f211"),
            num_subject=school_info.get("num_subject"),
            num_master=school_info.get("num_master"),
            num_doctor=school_info.get("num_doctor"),
            num_academician=school_info.get("num_academician"),
            num_lab=school_info.get("num_lab"),
            create_date=school_info.get("create_date"),
            area=school_info.get("area"),
            logo='https://static-data.eol.cn' + school_info.get("logo", '').replace('/app/html', ''),
            school_type_name=school_info.get("school_type_name"),
            school_nature_name=school_info.get("school_nature_name"),
            level_name=school_info.get("level_name"),
            type_name=school_info.get("type_name"),
            dual_class_name=school_info.get("dual_class_name"),
            short=school_info.get("short"),
            email=school_info.get("email"),
            school_email=school_info.get("school_email"),
            address=school_info.get("address"),
            site=school_info.get("site"),
            school_site=school_info.get("school_site"),
            phone=school_info.get("phone"),
            school_phone=school_info.get("school_phone"),
            content=school_info.get("content"),
            content_detail=school_detail.get("content"),

        )

        self.mongo.write_school_info([data])
        self.mongo.conn.close()


if __name__ == '__main__':
    ce = CrawlerEol('清华大学')
    ce.start()
