import re, requests, time, json, pymongo
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dierzhou.YDM import get_ma


class MyWenSHu(object):
    def __init__(self):
        # 存入mongo
        client = pymongo.MongoClient()
        self.wens = client['wens']['table']
        #定义session 请求方式
        self.session = requests.session()
        # 得到头部信息，cookie 尤为重要，约10分钟换一次  data里边的vl5x值相对应
        self.user_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36',
            'cookie': 'vjkl5=010AA1FF725F8A0140188AF2B2101C64DC39DC4E',
            'Referer': 'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+++2017-09-07%20TO%202017-09-08+%E4%B8%8A%E4%BC%A0%E6%97%A5%E6%9C%9F:2017-09-07%20TO%202017-09-08&conditions=searchWord+2+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E5%88%91%E4%BA%8B%E6%A1%88%E4%BB%B6'
            }

    def get_page(self, start_url):
        for page in range(1, 6):
            print('-'*26, '第%d页'%page, '-'*26)
            # 当请求第一页时
            if page == 1:
                # yanzheng = input('请输入验证码：')#原手动打码
                self.data = {
                    'Param': '上传日期:2017-09-08 TO 2017-09-09,案件类型:刑事案件',
                    'Index': page,
                    'Page': '5',
                    'Order': '法院层级',
                    'Direction': 'asc',
                    'vl5x': 'b55db3f3fcbfd24d3d6d418e',
                    'number': 'wens',
                    'guid': '//wenshu.court.gov.cn/List/List?sor'
                }
                r = self.session.post(url=start_url, headers=self.user_agent, data=self.data, timeout=10)
                r.encoding = r.apparent_encoding
                self.get_con(r.text)
            # 请求其他页时   由于第一页请求方式和其它页不同
            else:
                # print(ma)# 手动打码时需要点击的验证码
                ma = 'http://wenshu.court.gov.cn/ValiCode/CreateCode/?guid=c4d9104f-31dc-dcf52d41-14fc28993109'
                # 验证码下载，保存方式以打码名字命名
                re_ma = requests.get(ma).content
                with open('getimage.jpg','wb') as f:
                    f.write(re_ma)
                # yanzheng = input('请输入验证码：')
                data = {
                    'Param': '上传日期:2017-09-08 TO 2017-09-09,案件类型:刑事案件',
                    'Index': page,
                    'Page': '5',
                    'Order': '法院层级',
                    'Direction': 'asc',
                    'vl5x': 'b55db3f3fcbfd24d3d6d418e',
                    'number': get_ma(),
                    'guid': 'c4d9104f-31dc-dcf52d41-14fc28993109'
                }
                r = self.session.post(url=start_url, headers=self.user_agent, data=data, timeout=20)
                r.encoding = r.apparent_encoding
                print(r)
                self.get_con(r.text)

    def get_con(self, con):
        dict1 = {}
        json_str = json.loads(con)
        # 正则匹配 每个文书的ID
        rep_id= re.findall('"文书ID":"(.*?)"',json_str)
        # 正则匹配为列表 循环开 拼接data值
        dict2={}
        for i in rep_id:
            data = {
                'docId': i
            }

            con_url = 'http://wenshu.court.gov.cn/content/content?DocID='+ i
            dict1['URL'] = con_url
            # 找到内容的接口
            nei_url = 'http://wenshu.court.gov.cn/Content/GetSummary'
            r = requests.post(nei_url, data=data)
            r.encoding =r.apparent_encoding
            json_strs = json.loads(r.text)
            # 正则匹配出所有要的字段
            people = re.findall(' name: "(.*?)",.*?value: "(.*?)" ',json_strs)
            # 把内容加入到字典
            for n in people:
                dict1[n[0]] = n[1]
            dict2={'name':dict1}
            print(dict1)
            self.wens.insert_one(dict2)

    def main(self):
        start_url = 'http://wenshu.court.gov.cn/List/ListContent'
        self.get_page(start_url)


if __name__ == '__main__':
    spider = MyWenSHu()
    spider.main()
