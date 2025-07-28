import requests
import sys
# Add Google Sheets integration
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
 
def extract_shortcode_from_url(url):
    # Instagram post/reel URLs look like: https://www.instagram.com/reel/<shortcode>/ or https://www.instagram.com/p/<shortcode>/
    match = re.search(r"instagram.com/(?:reel|p)/([\w-]+)", url)
    if match:
        return match.group(1)
    return None
 
def get_sheet_links(sheet_path, spreadsheet_name, worksheet_name=None):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(sheet_path, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    if worksheet_name:
        sheet = spreadsheet.worksheet(worksheet_name)
    else:
        sheet = spreadsheet.sheet1
    # Assumes the column is named 'Links'
    links_col = sheet.find('Links').col
    comment_count_col = sheet.find('Actual Comment Count (Automation)').col
    links = sheet.col_values(links_col)[1:]  # skip header
    return sheet, links, links_col, comment_count_col
 
if __name__ == "__main__":
    # Default values for your setup
    DEFAULT_CREDS = 'credentials/creds.json'
    DEFAULT_SPREADSHEET = 'insta-comments-count'
    DEFAULT_WORKSHEET = 'Sheet1'
 
    # Use defaults if not enough arguments are provided
    sheet_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CREDS
    spreadsheet_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPREADSHEET
    worksheet_name = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_WORKSHEET
 
    sheet, links, links_col, comment_count_col = get_sheet_links(sheet_path, spreadsheet_name, worksheet_name)
    for idx, link in enumerate(links, start=2):  # start=2 to match sheet row numbers (skip header)
        shortcode = extract_shortcode_from_url(link)
        if not shortcode:
            print(f"Invalid Instagram link: {link}")
            continue
        url = "https://www.instagram.com/api/graphql"
        payload = f'av=0&__d=www&__user=0&__a=1&__req=2&__hs=19773.HYP%3Ainstagram_web_pkg.2.1..0.0&dpr=1&__ccg=UNKNOWN&__rev=1011518048&__s=y7v9z3%3Aasiqg7%3A5kmeai&__hsi=7337678488427234873&__dyn=7xeUjG1mxu1syUbFp40NonwgU29zEdEc8co2qwJw5ux609vCwjE1xoswaq0yE7i0n24oaEd86a3a1YwBgao6C0Mo2iyovw8O4U2zxe2GewGwso88cobEaU2eUlwhEe87q7U1bobpEbUGdwtU662O0Lo6-3u2WE5B0bK1Iwqo5q1IQp1yUoxe4Xxui2qi&__csr=gL3ltOOSGkBAqQGRXKihqKKblrSRrF4yFknGGgGFppVpv-mdKaBSiucXG8Diy8G7aJWyazemA-jAqBDxamqVGhVaUTjgDxmRjDjKVKmEGK6bgjzqz22Ukzefx2q2600kGuOU0I5z81340eiw1Sa4NdxC1fws80mu409q04w87G0k-lS0pV008A2&__comet_req=7&lsd=AVpv9-ZMTFc&jazoest=2903&__spin_r=1011518048&__spin_b=trunk&__spin_t=1708436405&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisPostActionLoadPostQueryQuery&variables=%7B%22shortcode%22%3A%22{shortcode}%22%2C%22fetch_comment_count%22%3A40%2C%22fetch_related_profile_media_count%22%3A3%2C%22parent_comment_count%22%3A24%2C%22child_comment_count%22%3A3%2C%22fetch_like_count%22%3A10%2C%22fetch_tagged_user_count%22%3Anull%2C%22fetch_preview_comment_count%22%3A2%2C%22has_threaded_comments%22%3Atrue%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D&server_timestamps=true&doc_id=10015901848480474'
        headers = {
          'authority': 'www.instagram.com',
          'accept': '*/*',
          'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
          'content-type': 'application/x-www-form-urlencoded',
          'cookie': 'csrftoken=BsnkufRG74SgG06CBbuRUY; mid=ZdSoNQAEAAHdyTBmytpDUO2ICnxE; ig_did=E9B90982-25F1-470F-80B1-895283FDCB58; ig_nrcb=1; datr=NKjUZUf2m5fUalhmfm7dB4dc; ps_l=0; ps_n=0',
          'dpr': '1',
          'origin': 'https://www.instagram.com',
          'referer': f'https://www.instagram.com/reel/{shortcode}/',
          'sec-ch-prefers-color-scheme': 'dark',
          'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
          'sec-ch-ua-full-version-list': '"Not A(Brand";v="99.0.0.0", "Google Chrome";v="121.0.6167.139", "Chromium";v="121.0.6167.139"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-model': '""',
          'sec-ch-ua-platform': '"macOS"',
          'sec-ch-ua-platform-version': '"14.3.0"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-origin',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
          'viewport-width': '1920',
          'x-asbd-id': '129477',
          'x-csrftoken': 'BsnkufRG74SgG06CBbuRUY',
          'x-fb-friendly-name': 'PolarisPostActionLoadPostQueryQuery',
          'x-fb-lsd': 'AVpv9-ZMTFc',
          'x-ig-app-id': '936619743392459'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        comment_count = ''
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("data"):
                edge_media = json_data["data"].get("xdt_shortcode_media", {})
                if edge_media.get("edge_media_to_parent_comment"):
                    comment_count = edge_media['edge_media_to_parent_comment'].get('count')
        # Write comment count to the sheet
        sheet.update_cell(idx, comment_count_col, comment_count)
        print(f"{link} -> {comment_count}")
