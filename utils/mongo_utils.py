import pymongo


class MongoDB(object):

    def __init__(self):
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % ("qzq1111", 'qzq1111', "localhost", "27017", "school_news_analysis")
        self.conn = pymongo.MongoClient(mongo_uri)
        self.db = self.conn.school_news_analysis

    def write_news(self, news):
        """
        写入新闻到mongodb,去重写入
        :param news:新闻列表
        :return:
        """
        school_news = self.db.school_news
        insert_data = list()
        for item in news:
            insert_data.append(pymongo.ReplaceOne({'news_link': item['news_link']}, item, upsert=True))
        school_news.bulk_write(insert_data)

    def write_school_info(self, school):
        """
        写入学校信息到数据库，去重写入
        :param school:
        :return:
        """
        school_info = self.db.school_info
        insert_data = [pymongo.ReplaceOne({'school_code': school['school_code']}, school, upsert=True)]
        school_info.bulk_write(insert_data)
