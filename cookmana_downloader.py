import requests, re, os, tqdm

def init():

    print("----------------------------------")
    print("쿡마나 다운로더 Update 2024.06.03")
    print("----------------------------------")

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

if __name__ == '__main__':

    init()
    
    url = input("다운로드할 만화의 URL을 입력하세요(e.g. http://154.219.3.228/episode/2498?order=desc) ")

    # url에서 숫자로된 id 부분을 추출
    manga_id = re.search(r'episode/(\d+)', url).group(1)


    # API 요청으로 만화 정보 가져오기
    info_api_url = f"http://154.219.3.228/api/episode/cover/{manga_id}"
    response = requests.get(info_api_url)
    data = response.json()  
    manga_title = data['data']['title']

    manga_list = []

    # API 요청으로 목록 가져오기
    for page in range(100):
        list_api_url = f"http://154.219.3.228/api/episode/list/{manga_id}?page={page+1}&order=desc"
        response = requests.get(list_api_url)

        data = response.json()
        if len(data['data']) == 0: # 마지막 페이지인 경우
            break

        manga_list.extend(data['data'])

    manga_list.reverse()

    index = 0

    for manga in tqdm.tqdm(manga_list, desc=f"{manga_title} 다운로드 중"):
        index += 1
        episode_id = manga['id']
        title = manga['title']
        title = str(index).zfill(3) + "_" + title


        # 이미 다운로드한 화인지 확인
        dirname = f"downloads/{manga_title}/{title}"
        if os.path.exists(dirname):
            print(f"{title}은 이미 다운로드한 화입니다.")
            continue

        # 각 화별 API 요청으로 이미지 목록 가져오기
        image_api_url = f"http://154.219.3.228/api/detail/{episode_id}"
        response = requests.get(image_api_url)
        data = response.json()
        image_urls = data['data']['urls'].split(",")
        
        serverType = "01"
        for i, image_url in enumerate(tqdm.tqdm(image_urls, desc=f"{title} 다운로드 중")):

            if not "/" in image_url:
                image_download_url = f"http://www.pl3040.com//kr/{serverType}/{manga_id}/{episode_id}/{image_url}"
            else:
                A, B, C = image_url.split("/")
                image_download_url = f"http://www.pl3040.com//kr/{serverType}/{manga_id}/{episode_id}/{C}"

            # Check serverType
            res = requests.get(image_download_url)
            if res.status_code != 200:
                if serverType == "01":
                    serverType = "02"
                else:
                    serverType = "01"
                
                if not "/" in image_url:
                    image_download_url = f"http://www.pl3040.com//kr/{serverType}/{manga_id}/{episode_id}/{image_url}"
                else:
                    A, B, C = image_url.split("/")
                    image_download_url = f"http://www.pl3040.com//kr/{serverType}/{manga_id}/{episode_id}/{C}"


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
            
