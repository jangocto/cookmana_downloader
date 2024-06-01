import requests, re, os

def init():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

if __name__ == '__main__':

    init()
    
    url = input("다운로드할 만화의 URL을 입력하세요(e.g. http://154.219.3.228/episode/2498?order=desc)")

    # url에서 숫자로된 id 부분을 추출
    manga_id = re.search(r'episode/(\d+)', url).group(1)


    # API 요청으로 만화 정보 가져오기
    info_api_url = f"http://154.219.3.228/api/episode/cover/{manga_id}"
    response = requests.get(info_api_url)
    data = response.json()  
    manga_title = data['data']['title']


    # API 요청으로 목록 가져오기
    list_api_url = f"http://154.219.3.228/api/episode/list/{manga_id}?page=1&order=desc"

    response = requests.get(list_api_url)
    data = response.json()

    manga_list = data['data']
    manga_list.reverse()

    for manga in manga_list:
        episode_id = manga['id']
        title = manga['title']

        # 이미 다운로드한 화인지 확인
        dirname = f"downloads/{manga_title}/{title}"
        if os.path.exists(dirname):
            print(f"{title}은 이미 다운로드한 화입니다.")
            continue

        print(f"Downloading {title}...")

        # 각 화별 API 요청으로 이미지 목록 가져오기
        image_api_url = f"http://154.219.3.228/api/detail/{episode_id}"
        response = requests.get(image_api_url)
        data = response.json()
        image_urls = data['data']['urls'].split(",")
        
        for i, image_url in enumerate(image_urls):
            if not "/" in image_url:
                image_download_url = f"http://www.pl3040.com//kr/02/{manga_id}/{episode_id}/{image_url}"
            else:
                A, B, C = image_url.split("/")
                image_download_url = f"http://www.pl3040.com//kr/02/{A}/{episode_id}/{C}"
            print(f"Downloading {i+1}/{len(image_urls)}... {image_download_url}")
    
            dirname = f"downloads/{manga_title}/{title}"
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            
            response = requests.get(image_download_url)
            status_code = response.status_code
            if status_code != 200:
                print(f"Failed to download {image_download_url} (status code: {status_code})")
                continue
            with open(f"{dirname}/{i+1}.jpg", 'wb') as f:
                f.write(response.content)

    print("다운로드 완료!")
            