import requests
import random
from lxml import html
import time
import csv
import re
import json
class BiliSpider:
    def __init__(self):
        self.url="https://www.bilibili.com/v/popular/rank/all"
        self.movie_url='https://www.bilibili.com/v/popular/rank/movie'
        self.headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
        self.proxies=['183.47.237.251:80','122.226.57.70:8888','121.8.146.99:8060','183.47.237.251:80']
        self.f=open("Bili-Rank.csv",'w',newline='',encoding='utf-8-sig',errors='ignore')
        self.writer=csv.writer(self.f)
        self.writer.writerow(['name','viewer','bullets','score','author','like','coin','collect','share','tag'])
        self.movie=open("Movie-Rank.csv","w",newline='',encoding='utf-8-sig',errors='ignore')
        self.movie_writer=csv.writer(self.movie)
        self.movie_writer.writerow(['name','Comprehensive_score','like','viewer','bullets','coin','showtime','follower','voter','score','tag'])
        #self.f.close()

    def get_ip(self):
        #IP池，banIP时用
        ip=random.choice(self.proxies)
        proxies={'http':'http://'+ip,
                 'https':'https://'+ip}
        return proxies


    def get_movie_first_html(self):
        #电影TOP100信息：链接 名称 观看人数 弹幕数 分数 上映日期 追剧人数
        movie_rank_hrml=requests.get(url=self.movie_url,headers=self.headers).text
        e=html.etree
        eobj=e.HTML(movie_rank_hrml)
        href_list=eobj.xpath('//div[@class="info"]/a/@href')
        name_list = eobj.xpath('//div[@class="info"]/a/text()')
        viewer_list = eobj.xpath('//div[@class="detail"]/span[1]/text()')
        bullets_list = eobj.xpath('//div[@class="detail"]/span[2]/text()')
        score_list = eobj.xpath('//div[@class="pts"]/div/text()')
        showtime_list=eobj.xpath('//div[@class="pgc-info"]/text()')
        follower_list=eobj.xpath('//div[@class="detail"]/span[3]/text()')
        tmp=-1
        for href in href_list:
            tmp+=1
            score,voter,like,coin,tag=self.get_movie_html(href)
            viewer=self.remove_str(viewer_list[tmp])
            bullets = self.remove_str(bullets_list[tmp])
            follower=self.remove_str(follower_list[tmp])
            if len(showtime_list[tmp])<6:
                showtime=showtime_list[tmp]
            else:
                showtime=showtime_list[tmp][:-2]
            self.movie_save(name_list[tmp],viewer,bullets,score_list[tmp],showtime,follower,score,voter,like,coin,tag)
            print('ok',name_list[tmp])
            time.sleep(random.randint(1,3))
        self.movie.close()

    def movie_save(self,name,viewer,bullets,score,showtime,follower,Comprehensive_score,voter,like,coin,tag):
        #存入csv
        self.movie_writer.writerow([name,Comprehensive_score,like,viewer,bullets,coin,showtime,follower,voter,score,tag])


    def get_movie_html(self,href):
        #获得异步传输文件内的信息：点赞数和硬币数
        #print(href)
        #为获取异步文件做准备，这步是通过二级页面的url获得电影id
        regex="""www.bilibili.com/bangumi/play/.*?ss(.*)\?"""
        para=re.findall(regex,href)
        #print(para)
        #异步文件的url是固定前缀配上电影id
        movie_url='https://api.bilibili.com/pgc/web/season/stat?season_id='+para[0]
        #观察后发现得到一个字典样式的字符串，用json改为字典就可以轻松获取数据
        movie_html=requests.get(url=movie_url,headers=self.headers).text
        movie_dict=json.loads(movie_html)
        like=movie_dict['result']['likes']
        coin = movie_dict['result']['coins']
        # 获得电影详情页信息：综合分数 评分人数
        url='https:'+href
        html1=requests.get(url=url,headers=self.headers).text
        e=html.etree
        movie_eobj=e.HTML(html1)
        score=movie_eobj.xpath('//h4[@class="score"]/text()')
        tag_url=movie_eobj.xpath('//a[@class="media-cover"]/@href')
        tag=self.get_movie_tag(tag_url)
        voter=[]
        #部分电影评分人数太少，没有分数，写入None
        if score:
            voter = movie_eobj.xpath('//div[@class="media-rating"]/p/text()')
            return score[0], self.remove_str(voter[0][:-3]), like, coin,tag
        else:
            score1='None'
            voter1='None'
            return score1, voter1, like, coin,tag

    def get_movie_tag(self,url):
        #第三重网页，用于获取电影的类别
        tag_url='https:'+url[0]
        html1=requests.get(url=tag_url,headers=self.headers).text
        e=html.etree
        tag_eobj=e.HTML(html1)
        tag_list=tag_eobj.xpath('//span[@class="media-tag"]/text()')
        tag_mes=''
        if tag_list:
            for tag in tag_list:
                tag_mes=tag_mes+' '+tag
        else:
            tag_mes='None'
        return tag_mes.strip()

    def get_first_html(self):
        #得到热门视频TOP100信息：链接 名称 观看人数 弹幕数 分数 作者
        html1=requests.get(url=self.url,headers=self.headers).text
        #print(html)
        e=html.etree
        eobj=e.HTML(html1)
        href_list=eobj.xpath('//div[@class="info"]/a/@href')
        name_list=eobj.xpath('//div[@class="info"]/a/text()')
        viewer_list=eobj.xpath('//div[@class="detail"]/span[1]/text()')
        bullets_list=eobj.xpath('//div[@class="detail"]/span[2]/text()')
        score_list=eobj.xpath('//div[@class="pts"]/div/text()')
        author_list=eobj.xpath('//span[@class="data-box up-name"]/text()')
        tmp=-1
        for href in href_list:
            tmp = tmp + 1
            # if tmp<73:
            #     continue
            like,coin,collect,share,tag=self.get_second_html(href)
            viwer=self.remove_str(viewer_list[tmp])
            bullets=self.remove_str(bullets_list[tmp])
            self.save_to_csv(name_list[tmp],viwer,bullets,score_list[tmp],author_list[tmp].strip(),like,coin,collect,share,tag.strip())

            print('ok',name_list[tmp])
            time.sleep(random.randint(1,3))
        self.f.close()
            # if tmp==70:
            #      break


    def get_second_html(self,href):
        #获得视频详情页信息：硬币 点赞 收藏 分享 标签
        video_url='https:'+href
        video_html=requests.get(url=video_url,headers=self.headers).content.decode('utf-8')
        e=html.etree
        video_eboj=e.HTML(video_html)
        #部分视频属于官方综艺，代码格式不同并且数量极少，直接用None替代
        like=video_eboj.xpath('//span[@class="like"]/text()')
        like=like if like else ['None']
        like_int=self.remove_str(like[0])
        coin=video_eboj.xpath('//span[@class="coin"]/text()')
        coin = coin if coin else ['None']
        coin_int = self.remove_str(coin[0])
        collect=video_eboj.xpath('//span[@class="collect"]/text()')
        collect = collect if collect else ['None']
        collect_int = self.remove_str(collect[0])
        share=video_eboj.xpath('//span[@class="share"]/text()')
        share = share if share else ['None']
        share_int = self.remove_str(share[0])
        #视频标签不知为什么有两种写法，一个放在span里，一个放在a里，这里全部取来
        tag1=video_eboj.xpath('//a[@class="tag-link"]/span/text()')
        tag2=video_eboj.xpath('//a[@class="tag-link"]/text()')
        mes_tag=''
        if len(tag1) | len(tag2):
            if tag1:
                for t in tag1:
                    mes_tag = mes_tag+' '+t.strip()
            if tag2:
                for t in tag2:
                    mes_tag = mes_tag + ' ' + t.strip()
        else:
            mes_tag='None'
        return like_int,coin_int,collect_int,share_int,mes_tag

    def save_to_csv(self,name,viewer,bullets,score,author,like,coin,collect,share,tag):
        #存储到csv
         self.writer.writerow([name,viewer,bullets,score,author,like,coin,collect,share,tag])

    def remove_str(self,remove):
        #上万的数据在页面里以‘xxx万’的形式呈现，为了数据分析人员的方便，避免再区分str和int，写了这个函数用来去掉‘万’，将str变为int
        if '万' in remove:
            remove_int=remove.strip()
            remove_int=int(float(remove_int[:-1])*10000)
            return remove_int
        return remove.strip()
if __name__ == '__main__':
    #主函数
    Bi=BiliSpider()
    Bi.get_first_html()
    Bi.get_movie_first_html()
