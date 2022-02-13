import scrapy
import re
import unicodedata
import urllib.parse
import inquirer

class HelloworkSpider(scrapy.Spider):
    name = 'hellowork'

    def __init__(self):
        pref = ['北海道', '青森', '岩手', '宮城', '秋田' ,'山形', '福島', '茨城' , '栃木', '群馬', '埼玉', '千葉', '東京','神奈川', '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡', '愛知', '三重', '滋賀', '京都', '大阪', '兵庫','奈良', '和歌山', '鳥取', '島根', '岡山', '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分', '宮崎', '鹿児島', '沖縄']
        question1 = [inquirer.List(
            '都道府県',
            message = '都道府県選択',
            choices = pref
        ),
        ]
        answer1 = inquirer.prompt(question1)
        self.prefecture = answer1['都道府県']
        self.parse_prefecture = urllib.parse.quote(self.prefecture)
        self.start_urls = [f'https://www.hellowork.careers/%E6%B1%82%E4%BA%BA?q=&l={self.parse_prefecture}&only_hellowork=c&start=' + str(i) for i in range(0, 1000,20)]

    def parse(self, response):

        for row in response.css('.row'):
            payment_list = ['月給', '時給', '日給', '相談', '案件毎','出来高制月収','１件', '年俸', '完全出来高制', '完全出来高制例）' , '歩合制60％', '出来高制', '能力給、経験等を考慮基本給（2万円）＋成功報酬' ,'歩合']
            contract_list = ['派遣', '正社員', '正社員', 'アルバイト・パート', 'パート・アルバイト' ,'契約社員' , '業務委託' , 'レギュラー', '正社員以外', 'パート労働者',  '無期雇用派遣労働者' , '有期雇用派遣労働者', '有期雇用派遣パート', 'アルバイト' , 'パート']

            salaryinfo1 = row.css('.snip ::text')[0].get()
            salaryinfo2 = row.css('.snip ::text')[1].get()
            salaryinfo3 = row.css('.snip ::text')[2].get()
            salaryinfo = salaryinfo1 + salaryinfo2 + salaryinfo3
            s = salaryinfo.strip()
            s = s.replace(' ', '')
            s = s.replace(',', '')
            s = s.replace('～', '-')

            pattern1 = re.compile(r'[0-9]+万円以上+-[0-9]+万円以上')
            pattern2 = re.compile(r'[0-9]+円以上')  
            pattern3 = re.compile(r'[0-9]+円+-[0-9]+円')
            pattern4 = re.compile(r'[0-9]+円')  
            pattern5 = re.compile(r'[0-9]+万円+-[0-9]+万円')
            pattern6 = re.compile(r'[0-9]+万円以上')
            pattern7 = re.compile(r'[0-9]+万円')

            pattern_list = [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7]

            try:
                title = row.css('.jobtitle')
                url = title.css('a::attr(href)').get()
            except:
                url =''

            try:

                arr = []
                for payment_type in payment_list:
                    payment_type_pattern =  re.compile(rf'{payment_type}')
                    matches = payment_type_pattern.finditer(s)
                    for match in matches:
                        res = match.span()
                        arr.append(res)

                payment_first = arr[0][0]
                payment_last = arr[0][1]

                payment =s[payment_first:payment_last]
            except:
                payment = ''


            try:
                arr = []
                for pattern in pattern_list:
                    matches = pattern.finditer(s)
                    for match in matches:
                        res = match.span()
                        arr.append(res)

                pattern_first = arr[0][0]
                pattern_last = arr[0][1]
                salary = s[pattern_first:pattern_last]

            except:

                salary = ''
            try:

                arr = []
                for contract_type in contract_list:
                    contract_type_pattern =  re.compile(rf'{contract_type}')
                    matches = contract_type_pattern.finditer(s)
                    for match in matches:
                        res = match.span()
                        arr.append(res)
                contract_first = arr[0][0]
                contract_last = arr[0][1]

                contract =s[contract_first:contract_last]
               
  
            except:
                contract = ''

            try:
                date = row.css('.date ::text').get() 
                date = date.strip()
                date.replace('\\xa0', ' ')

                new_str = unicodedata.normalize("NFKD", date)
                date =new_str.split(' ')
                new = date[0].split(':')
                if new[0] == '受理日':
                    date = new[1]
                else:
                    date = new[0] 

            except:
                date = ''
            try:
                reply_limit = row.css('.reply-limit ::text')[0].get()
                reply_limit = reply_limit.replace('までに結果通知が届きます', '')

            except:
                reply_limit =''

            work     = row.css('.jobtitle ::text')[0].get()
            name     = row.css('.company ::text')[0].get()
            location = row.css('.location ::text')[0].get()
            origin   = row.css('.sdn ::text')[0].get()

            yield scrapy.Request(url, callback=self.get_phone_number, meta = {
                'work': work, 
                'name': name,
                'location': location,
                'payment': payment,
                'salary': salary,
                'contract': contract,
                'origin': origin,
                'date': date,
                'reply_limit': reply_limit

            })
 


    def get_phone_number(self, response):

        work = response.meta['work']
        name = response.meta['name']
        location = response.meta['location']
        payment = response.meta['payment']
        salary = response.meta['salary']
        contract = response.meta['contract']
        origin = response.meta['origin']
        date = response.meta['date']
        reply_limit = response.meta['reply_limit']

        current_url = response.request.url

        phoneinfo = response.css('.jddl-pdleftg0 ::text').getall()
        try:
            if '電話番号' in phoneinfo:
                l = [phoneinfo.index(i) for i in phoneinfo if '電話番号' in i]
                num = l[0] + 2
                phonenumber = phoneinfo[num]
            else:
                phonenumber = ''
        except:
            phonenumber = ''

        yield{
                '仕事' :work,
                '会社名' : name,
                'url': current_url,
                '場所' : location,
                '給料形態' : payment,
                '金額' : salary,
                '契約形態' : contract,
                '掲載元' : origin,
                '掲載日':  date,
                '結果通知期限' : reply_limit,
                '電話番号':phonenumber
        }

        return



        



