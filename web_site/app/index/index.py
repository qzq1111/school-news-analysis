from flask import Blueprint, render_template, request, jsonify

from utils.mongo_utils import MongoDB

index_bp = Blueprint('index', __name__)


@index_bp.route('/', methods=['GET'])
def index():
    key = '北京戏曲艺术职业学院'
    mongo = MongoDB()
    # ------------------------- 查询基本信息 ----------------------#
    school_info = mongo.db.school_info.find_one({'name': key}, {"_id": 0, })

    # ------------------------- 查询新闻 ------------------------#
    time_count_data = mongo.db.school_news.aggregate(
        [{"$match": {"news_key": key}},
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

    news_author_count = mongo.db.school_news.aggregate(
        [
            {"$match": {"news_key": key}},
            {"$group": {"_id": {"news_author": '$news_author'}, 'value': {"$sum": 1}}},
            {"$project": {'_id': 0, 'name': '$_id.news_author', 'value': 1}},
            {"$sort": {"value": -1}},
            {"$limit": 10}

        ]
    )
    # news_data = mongo.db.school_news.find({"news_key": '清华大学'},
    #                                       {"_id": 0, "news_title": 1, "news_author": 1, "news_time": 1, "news_link": 1}
    #                                       ).sort([("news_time", -1)]).limit(20)
    # data_count = mongo.db.school_news.find({"news_key": '清华大学'},
    #                                        {"_id": 0, "news_title": 1, "news_author": 1, "news_time": 1, "news_link": 1}
    #                                        ).count()
    return render_template('index.html', news_data_count=news_data_count,
                           news_data_time=news_data_time,
                           news_author_count=list(news_author_count),
                           school_info=school_info
                           )


@index_bp.route('/nextPage', methods=["GET"])
def next_page():
    """
    获取下一页
    :return:
    """
    page = request.args.get('page', 1, type=int)
    mongo = MongoDB()
    news_data = mongo.db.school_news.find({"news_key": '清华大学'},
                                          {"_id": 0, "news_title": 1, "news_author": 1, "news_time": 1, "news_link": 1}
                                          ).sort([("news_time", -1)]).skip(20 * (page - 1)).limit(20)

    return jsonify(list(news_data))
