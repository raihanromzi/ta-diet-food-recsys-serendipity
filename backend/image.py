from google_images_search import GoogleImagesSearch

def get_image_url(query: str) -> str:
    gis = GoogleImagesSearch('AIzaSyDHuSqbBG0RSRQiDYPFYw6_2-yGZFUuS5g', '90f5945524c6643aa')

    _search_params = {
        'q': query,
        'num': 1,
        'safe': 'high',
        'fileType': 'jpg|png|jpeg',
        'imgType': 'photo',
        'imgSize': 'medium',
    }

    gis.search(search_params=_search_params)
    if gis.results():
        return gis.results()[0].url
    return 'No image found'
