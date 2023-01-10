import logging
# from telegram import Update
# from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import requests
from  bs4  import  BeautifulSoup  as  bs
import  schedule
import  time
from get_stock import get_stocks


TOKEN = "5893171109:AAEgunTsyUkxEqqNKKLbq6kihVfMnHb6Xbw"
CHAT_ID = "1099791233"



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def send_telegram_message(text):
    send_api = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&text=' + text
    r = requests.get(send_api)
    print (r.json())

def get_new_links(query, old_links=[]):

    # (주의) 네이버에서 키워드 검색 - 뉴스 탭 클릭 - 최신순 클릭 상태의 url
    url = f'https://search.naver.com/search.naver?where=news&query={query}&sm=tab_opt&sort=1&photo=0&field=0&pd=7&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0'

    # html 문서 받아서 파싱(parsing)
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')

    # 해당 페이지의 뉴스기사 링크가 포함된 html 요소 추출
    news_titles = soup.select('a.news_tit')

    # 요소에서 링크만 추출해서 리스트로 저장
    list_links = [i.attrs['href'] for i in news_titles]

    # 기존의 링크와 신규 링크를 비교해서 새로운 링크만 저장
    new_links = [link for link in list_links if link not in old_links]

    return new_links

def send_links(query):
    # 함수 내에서 처리된 리스트를 함수 외부에서 참조하기 위함
    global old_links

    # 위에서 정의했던 함수 실행
    new_links = get_new_links(query, old_links)

    # 새로운 메시지가 있으면 링크 전송
    if new_links:
        send_telegram_message(text='방금 업데이트 된 ' + f"{query} 주제의 크롤링입니다.")
        for link in new_links:
            send_telegram_message(text=link)

    # 없으면 패스
    else:
        pass

    # 기존 링크를 계속 축적하기 위함

    old_links += new_links.copy()
    old_links +=  new_links.copy()


if __name__ == '__main__':
    # application = ApplicationBuilder().token('5893171109:AAEgunTsyUkxEqqNKKLbq6kihVfMnHb6Xbw').build()
    
    # start_handler = CommandHandler('start', start)
    # application.add_handler(start_handler)
    # application.add_handler(start_handler)
    
    # application.run_polling()


    kospi= get_stocks("kospi")
    kosdaq = get_stocks("kosdaq")
    print(type(kospi))
    company = kospi + kosdaq
    # company = ["BYD"]  # 테스트
    key_word = ["매각", "인수", "경영권 분쟁"]
    queries = []
    for i in company:
        for j in key_word:
            queries.append(i+' '+j)
    print(queries)
        
    # queries = ["부동산", "경제", "날씨"]

    for query in queries:

        # 위에서 얻은 chat id로 bot이 메세지를 보냄.
        # send_telegram_message(text=f"{query}를 주제로 뉴스 기사 크롤링이 시작 되었습니다")

        # step5.기존에 보냈던 링크를 담아둘 리스트 만들기
        old_links = []

        # 주기적 실행과 관련된 코드 (hours는 시, minutes는 분, seconds는 초)
        job = schedule.every(60).minutes.do(send_links, query)

    while True:
        schedule.run_pending()
        time.sleep(1)