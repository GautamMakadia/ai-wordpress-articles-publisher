import requests
import webbrowser
import asyncio
import markdown
import os
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
import re
import unicodedata

load_dotenv()

def sanitize_filename(name: str, replacement: str = "_", max_length: int = 255) -> str:
    # Normalize unicode characters (é → e)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")

    # Remove invalid characters
    name = re.sub(r"[<>:\"/\\|?*\x00-\x1F]", replacement, name)

    # Remove leading/trailing whitespace and dots
    name = name.strip().strip(".")

    # Collapse multiple replacements
    name = re.sub(rf"{re.escape(replacement)}+", replacement, name)

    # Truncate to max length
    return name[:max_length]


# === CONFIG ===
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = "https://localhost/"

client = genai.Client()

loop = asyncio.new_event_loop()

# === STEP 1: Open Browser to Log In and Authorize ===
def get_authorization_code():
    auth_url = f"https://public-api.wordpress.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=global"
    
    print("🔗 Opening browser to authorize...")
    webbrowser.open(auth_url)
    print("⚠️ After login, copy the 'code' from the redirected URL")
    code = input("Paste the 'code' parameter from the URL: ").strip()

    return code


# === STEP 2: Exchange Code for Access Token ===
def get_access_token(auth_code):
    token_url = "https://public-api.wordpress.com/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": auth_code
    }
    r = requests.post(token_url, data=payload)
    r.raise_for_status()
    return r.json()["access_token"]


# === STEP 3: Get Your Site ID ===
def get_site_id(access_token):
    r = requests.get("https://public-api.wordpress.com/rest/v1.1/me/sites", headers={
        "Authorization": f"Bearer {access_token}"
    })
    r.raise_for_status()
    sites = r.json()["sites"]
    print("\n🔍 Your Sites:")
    for i, s in enumerate(sites):
        print(f"{i+1}. {s['name']} — {s['URL']}")
    index = int(input("Enter the number of the site to post to: ")) - 1
    return sites[index]["ID"]


# === STEP 4: Generate Article from Title ===
async def generate_article(input_title):
    prompt = f"""
    Create blog article on "{input_title}" targeted at developers and students and working professionals.
    - Use markdown formatting: headings (#), 
    - bullet points, 
    - and code blocks (```python).
    - Keep it 800 to 1200 words.
    - Don't use emojis.
    """

    message = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    content_md = message.text
    lines = content_md.strip().split('\n')
    
    gen_title = ""
    markdown_body = content_md
    # Extract the title from the markdown article (assume first line is # Title)

    if lines and lines[0].startswith("#"):
        gen_title = lines[0].lstrip('#').strip()
        markdown_body = '\n'.join(lines[1:])
    else:
        gen_title = input_title.strip()

    return gen_title, markdown_body


# === STEP 5: Convert Markdown to WordPress HTML ===
def markdown_to_wp_html(md_text):
    html = markdown.markdown(md_text, extensions=['fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', '5']):
        tag.name = 'h5'
        tag['class'] = tag.get('class', []) + ['wp-block-heading']
    

    for pre in soup.find_all('pre'):
        pre['class'] = pre.get('class', []) + ['wp-block-code']
        if not pre.find('code'):
            code_tag = soup.new_tag('code')
            code_tag.string = pre.string or ''
            pre.clear()
            pre.append(code_tag)
    

    for ul in soup.find_all('ul'):
        ul['class'] = ul.get('class', []) + ['wp-block-list']
    

    return str(soup)


# === STEP 6: Post Article to WordPress ===
def post_to_wordpress(site_id, title, content_html, access_token):
    post_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_id}/posts/new"
    payload = {
        "title": title,
        "content": content_html,
        "status": "publish"
    }
    r = requests.post(post_url, headers={
        "Authorization": f"Bearer {access_token}"
    }, json=payload)

    if r.ok:
        print(f"\n✅ Article posted at: {r.json()['URL']}")
    else:
        print("❌ Failed to post")
        print(r.text)


async def fetch_and_publish(title, access_token, site_id):
    print(f"Generating article for : ({title}) ...")
    new_title, markdown_article = await generate_article(title)
    
    print(f"Parsing the article form responce and converting to html ({title})...")
    content_html = markdown_to_wp_html(markdown_article)

    file_name = sanitize_filename(new_title)
    print(f"saving content to file. ({title}) --> ./articles/{file_name}")
    with open("./articles/"+file_name, 'w') as f:
        f.write(new_title)
        f.write(content_html)


    print(f"Uploading to wordpress ({title}) ...")
    post_to_wordpress(site_id, new_title, content_html, access_token)

    print(f"Finish Generating. ({title})")


# === MAIN ===
async def main():
    code = get_authorization_code()
    access_token = get_access_token(code)
    site_id = get_site_id(access_token)

    titles = [
        #put your titles here with comma(,) seprated
    ]

    tasks = []

    for title in titles: # run concurrently, all artical generated at the same time
        tasks.append(
            asyncio.create_task(
                fetch_and_publish(
                    title=title, 
                    access_token=access_token, 
                    site_id=site_id
                )
            )
        )    
        
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
