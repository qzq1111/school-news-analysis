from flask import Blueprint, render_template, request

from utils.mongo_utils import MongoDB

index_bp = Blueprint('index', __name__)


@index_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@index_bp.route('/crawler', methods=["GET", "POST"])
def crawler():
    """
    抓取
    :return:
    """

    if request.method == "GET":
        return render_template('crawler_index.html')
    else:
        return "1"


@index_bp.route('/analysis', methods=["GET", "POST"])
def analysis():
    """
    抓取
    :return:
    """
    if request.method == 'GET':

        return render_template('analysis_index.html')
    elif request.method == 'POST':
        data = request.form.get("school_name")
        if data:
            return school_analysis(data)
        else:
            return render_template('analysis_index.html')
    else:
        return render_template('analysis_index.html')


def school_crawler(school):
    """

    :param school:
    :return:
    """
    return "1"


def school_analysis(school):
    """
      获取学校分析情况
      :param school:
      :return:
      """

    mongo = MongoDB()
    # ------------------------- 查询基本信息 ----------------------#
    school_info = mongo.db.school_info.find_one({'name': school}, {"_id": 0, })

    # ------------------------- 查询新闻 ------------------------#
    # 按照时间统计新闻数据
    time_count_data = mongo.db.school_news.aggregate(
        [{"$match": {"news_key": school}},
         {"$group": {"_id": {"news_time": '$news_time'}, 'count': {"$sum": 1}}},
         {"$project": {'_id': 0, 'news_time': '$_id.news_time', 'count': 1}},
         {"$sort": {"news_time": 1}},
         ]
    )
    news_data_count = list()
    news_data_time = list()
    for item in time_count_data:
        news_data_count.append(item['count'])
        news_data_time.append(item['news_time'])

    # 新闻按照发布者统计
    news_author_count = mongo.db.school_news.aggregate(
        [
            {"$match": {"news_key": school}},
            {"$group": {"_id": {"news_author": '$news_author'}, 'value': {"$sum": 1}}},
            {"$project": {'_id': 0, 'name': '$_id.news_author', 'value': 1}},
            {"$sort": {"value": -1}},
            {"$limit": 10}

        ]
    )
    # 新闻总数统计
    data_count = mongo.db.school_news.find({"news_key": school},
                                           {"_id": 0, "news_title": 1, }
                                           ).count()

    return render_template('school.html', news_data_count=news_data_count,
                           news_data_time=news_data_time,
                           news_author_count=list(news_author_count),
                           school_info=school_info,
                           data_count=data_count
                           )
