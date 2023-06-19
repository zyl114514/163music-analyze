from flask import Flask, render_template, request
from jinja2 import Template
import requests
import matplotlib.pyplot as plt
from pylab import mpl
from pyecharts.charts import WordCloud
from wordcloud import WordCloud
import webbrowser
from alive_progress import alive_bar
import jieba
import datetime
# paddle.enable_static()
# jieba.enable_paddle()
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

# 定义文件路径和名称
html_file = "page5.html"
txt_file = "content.txt"

# 读取文本文件内容
with open(txt_file, "r") as file:
    content = file.read()

# 替换HTML文件的全部内容
with open(html_file, "w") as file:
    file.write(content)

# 所有数据集合的名称
playlists = [] # 用户歌单列表
likeList = []  # 歌曲以及歌曲id列表【（歌曲名，ID） 】
artistList = []  # 歌手以及歌手id列表【（歌手名，ID） 】
playRec = {}  # 听歌记录的列表（听歌次数，歌曲喜爱程度打分，歌曲名，歌手名，id）
artistDict = {}  # 歌手和每个歌手出现的次数字典
emoTagOfSongs = {}  # 歌曲以及对应的情绪标签的字典
QuFeng = {}  # 歌曲以及对应的曲风标签的字典
emoTags = {}  # 情绪标签和每个标签出现次数的字典
qfTags = {}  # 曲风标签和每个标签出现次数的字典
comments = {}  # 评论
urllist = []  # 推荐音乐url
userlist = []
agedict = {}
genderdict = {}


# 获取用户歌单（用户id）
def getUserPlaylist(userid):
    # 获取歌单url
    url = 'http://localhost:3000/user/playlist?uid=' + str(userid)
    r = requests.get(url)
    if r.status_code == 200:
        print('请求成功')  # HTTP请求的返回状态，200表示连接成功，404表示失败
    print('正在玩命分析，请稍后......')
    r.raise_for_status()  # 如果状态码返回不是200，抛出HTTPRError错误
    record = r.json()
    for playlist in record['playlist']:
        playlists.append(playlist['id'])


# 获取歌单详情（歌单ID，限制歌曲数目）
def getSongDetailOfList(listId, limit):
    # 获取歌单url
    url = 'http://localhost:3000/playlist/track/all?id=' + str(listId) + '&limit=' + str(limit) + '&offset=0'
    r = requests.get(url)  # 爬取收藏的歌单
    r.raise_for_status()  # 如果状态码返回不是200，抛出HTTPRError错误
    r.encoding = r.apparent_encoding  # 防止乱码
    Dict = r.json()  # 将歌单详情以json格式存储
    for song in Dict['songs']:  # 遍历歌单详情
        likeList.append((song['name'], song['id']))  # 将歌曲名和歌曲id存入列表
        artistList.append((song['ar'][0]['name'], song['ar'][0]['id']))  # 将歌手和歌手id存入列表
    # print(len(likeList))
    # print('\n')
    # print(artistList)
    # print('\n')
    # 将歌手和每个歌手出现的次数存入字典中
    for arti in artistList:
        if arti[0] in artistDict:
            artistDict[arti[0]] += 1
        else:
            artistDict[arti[0]] = 1


# 获取用户听歌记录并存入列表
def getUserRecord(UserId):
    url = 'http://localhost:3000/user/record?uid='+str(UserId)+'&type=0'
    r1 = requests.get(url)#爬取用户听歌记录
    record1 = r1.json()#将听歌记录以json格式存
    for data in record1['allData']:#遍历听歌记录储
        playRec[data['song']['name']] = data['playCount']#将听歌记录存入字典


# 获取歌单每首歌曲的情绪标签并存入字典
def getEmotionalTags():
    with alive_bar(len(likeList), force_tty=True) as bar:
        for song in likeList:
            url = 'http://localhost:3000/song/wiki/summary?id=' + str(song[1])
            r2 = requests.get(url)
            record2 = r2.json()
            emotaglist = []
            bar()
            try:
                for data in record2['data']['blocks'][1]['creatives'][1]['resources']:
                    emotaglist.append(data['uiElement']['mainTitle']['title'])
                emoTagOfSongs[song[0]] = emotaglist
            except:
                pass
    # print(emoTagOfSongs)


# 将歌曲以及对应的曲风标签存入字典
def getQuFengTags():
    with alive_bar(len(likeList), force_tty=True) as bar:
        for song in likeList:
            url = 'http://localhost:3000/song/wiki/summary?id=' + str(song[1])
            r2 = requests.get(url)
            record2 = r2.json()
            qflist = []
            bar()
            try:
                for data in record2['data']['blocks'][1]['creatives'][0]['resources']:
                    qflist.append(data['uiElement']['mainTitle']['title'])
                QuFeng[song[0]] = qflist
            except:
                pass
        # print(qufeng)


# 记录标签出现的次数
def CountTag(emoTagDict, QfTagDict):
    for tags in emoTagDict.values():
        for tag in tags:
            if tag in emoTags:
                emoTags[tag] += 1
            else:
                emoTags[tag] = 1
    # print(emoTags)
    for tags in QfTagDict.values():
        for tag in tags:
            if tag in qfTags:
                qfTags[tag] += 1
            else:
                qfTags[tag] = 1
    # print(qfTags)


# 获取歌曲评论并提取关键词
def getComment():
    with open('stop_words.txt', encoding='utf-8') as f:
        stopwords = f.readline()
    with alive_bar(len(likeList), force_tty=True) as bar:
        print('正在玩命获取歌曲评论，请稍后......')
        for song in likeList:
            url = 'http://localhost:3000/comment/music?id='+str(song[1])+'&limit=1'
            r = requests.get(url)
            record = r.json()
            bar()
            for info in record['hotComments']:
                seg_list = jieba.cut(info['content'])
                for word in seg_list:
                    if word not in stopwords and len(word) >= 2:
                        if word in comments:
                            comments[word] += 1
                        else:
                            comments[word] = 1


# 将时间戳形式变为年代
def get_generation(timestamp):
    if timestamp >= 0:
        birth_date = datetime.datetime.fromtimestamp(timestamp)
        birth_year = birth_date.year
    else:
        birth_year = 1

    if 1970 <= birth_year <= 1979:
        return "70后"
    elif 1980 <= birth_year <= 1989:
        return "80后"
    elif 1990 <= birth_year <= 1999:
        return "90后"
    elif 2000 <= birth_year <= 2009:
        return "00后"
    elif 2010 <= birth_year <= 2019:
        return "10后"
    else:
        return "未知"


# 获取爬取同好歌曲评论区用户数据，分析人群特点。
def getGroupCharacteristic():
    genderdict['男生'] = 0
    genderdict['女生'] = 0
    print('正在分析同好人群特点，请稍后......')
    for song in likeList:
        url = 'http://localhost:3000/comment/music?id='+str(song[1])+'&limit=1'
        r = requests.get(url)
        record1 = r.json()
        limit = 0
        for info in record1['hotComments']:
            userlist.append(info['user']['userId'])
            limit += 1
            if limit == 3:
                break
    with alive_bar(len(userlist), force_tty=True) as bar1:
        for Id in userlist:
            url = 'http://localhost:3000/user/detail?uid=' + str(Id)
            r = requests.get(url)
            record3 = r.json()
            try:
                age = get_generation(record3['profile']['birthday']/1000)
                gender = record3['profile']['gender']
                if age in agedict and age != '未知':
                    agedict[age] += 1
                else:
                    agedict[age] = 1
                if gender == 1:
                    genderdict['男生'] += 1
                if gender == 2:
                    genderdict['女生'] += 1
            except:
                pass
            bar1()


# 根据歌单中歌曲标签以及歌手偏好作出饼状图
def drawpie_from_dict(diclist, filename):
    location = 1
    for dicdata in diclist:
        by_value = sorted(dicdata.items(), key=lambda item: item[1], reverse=True)
        x = []
        y = []
        for d in by_value:
            x.append(d[0])
            y.append(d[1])
        plt.subplot(2, 2, location)
        plt.pie(y[0:8], labels=x[0:8], radius=2, autopct='%3.1f%%', textprops={'size': 6})
        location += 1
    plt.subplots_adjust(left=0.2, right=0.8,  bottom=0.12, top=0.85, wspace=1.5, hspace=0.8)
    plt.rcParams['figure.figsize'] = (10, 8)  # 2.24, 2.24 设置figure_size尺寸
    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.savefig(filename)
    plt.close()


# 根据歌单中歌曲标签以及歌手偏好作出柱状图
def drawbar_from_dict(dicdata, RANGE, heng=0):
    # dicdata：字典的数据。
    # RANGE：截取显示的字典的长度。
    # heng=0，代表条状图的柱子是竖直向上的。heng=1，代表柱子是横向的。考虑到文字是从左到右的，让柱子横向排列更容易观察坐标轴。
    by_value = sorted(dicdata.items(), key=lambda item: item[1], reverse=True)
    x = []
    y = []
    for d in by_value:
        x.append(d[0])
        y.append(d[1])
    plt.barh(x[0:RANGE], y[0:RANGE])
    plt.yticks(size=10)
    plt.xticks(size=7)
    plt.rcParams['figure.figsize'] = (10, 8)  # 2.24, 2.24 设置figure_size尺寸
    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.savefig("sin2.png")
    plt.close()
    return


# 根据歌单中歌曲标签以及歌手偏好作出词云图
def wc_from_word_count(word_count, file):
    font = r'C:\Windows\Fonts\simfang.ttf'
    wc = WordCloud(
        font_path=font,
        max_words=100,  # 最多显示词数
        # max_font_size=100,  # 字体最大值
        background_color="white",  # 设置背景为白色，默认为黑色
        width=1500,  # 设置图片的宽度
        height=960,  # 设置图片的高度
        margin=10  # 设置图片的边缘
    )
    wc.generate_from_frequencies(word_count)  # 从字典生成词云
    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭坐标轴
    plt.rcParams['figure.figsize'] = (10, 8)  # 2.24, 2.24 设置figure_size尺寸
    plt.rcParams['savefig.dpi'] = 500  # 图片像素
    plt.savefig(file)
    plt.close()
    # plt.show()  # 显示图像
    # wc.to_file(fp)  # 保存图片


# 根据偏好歌手、风格、标签等在自定歌单范围内搜索相关歌曲作推荐
def recommend_music(n):
    recommendlist = []
    most_singer = sorted(artistDict.items(), key=lambda item: item[1], reverse=True)
    most_emotag = sorted(emoTags.items(), key=lambda item: item[1], reverse=True)
    most_qftag = sorted(qfTags.items(), key=lambda item: item[1], reverse=True)
    for i in range(n):
        url = 'http://localhost:3000/cloudsearch?keywords='+str(most_singer[i])+str(most_emotag[0])
        r1 = requests.get(url)
        record = r1.json()
        recommendlist.append(record['result']['songs'][0]['id'])
    for ID in recommendlist:
        url = 'https://music.163.com/#/song?id='+str(ID)
        urllist.append(url)


# 将推荐歌曲的地址发送到html文件中
def send_to_html():
    # 定义三个URL变量
    url1 = urllist[0]
    url2 = urllist[1]
    url3 = urllist[2]

    with open("page5.html") as file:
        template = Template(file.read())

    rendered_html = template.render(url1=url1, url2=url2, url3=url3)

    with open("page5.html", "w") as file:
        file.write(rendered_html)

    print('ok')


a = 0
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    input_text = request.form['input_text']
    try:

        getUserPlaylist(input_text)

        for listid in playlists:
            getSongDetailOfList(listid, 200)

        getEmotionalTags()

        getQuFengTags()

        getComment()

        CountTag(emoTagOfSongs, QuFeng)

        getUserRecord(input_text)

        recommend_music(3)

        send_to_html()

        getGroupCharacteristic()

        print('分析完成！')

        dictlist1 = [artistDict, qfTags, emoTags]

        dictlist2 = [agedict, genderdict]

        drawpie_from_dict(dictlist1, 'sin.png')

        drawpie_from_dict(dictlist2, 'sin4.png')

        wc_from_word_count(emoTags, 'sin2.png')

        wc_from_word_count(comments, 'sin3.png')

        drawbar_from_dict(playRec, 9, heng=0)

        url = 'http://localhost:63342/pythonProject13/result.' \
              'html?_ijt=r7huoen7bgb1gdnfkcqcmkuln2&_ij_reload=RELOAD_ON_SAVE'

        webbrowser.open(url, new=1, autoraise=True)

    except:
        print("爬取失败")
    # 在这里将输入的字符存入 Python 的变量中
    return '输入的字符是：{}'.format(input_text)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
