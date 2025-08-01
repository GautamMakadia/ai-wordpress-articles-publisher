
### Install Dependencies
```sh
pip install requests markdown beautifulsoup4 google-genai dotenv
```

### Create `.env` file to store the enviroment variables.

```sh
CLIENT_ID = your_wordpress_client_id
CLIENT_SECRET = your_wordpress_client_secret
GEMINI_API_KEY = gemini_api_key
```

#### Geting the wordpress credentials
1. Go to https://developer.wordpress.com/apps/ 
2. Create new app or select the existing one.
3. You will get the `client_id` and `client_secret`
4. copy and past it inside `.env` variables


#### Getting the Gemini API Key
1. Go to the https://aistudio.google.com/app/apikey
2. Click on the `Create Api Key`.
3. Copy the key and past it inside the `.env`


### Run the program.
```sh
python main.py
```

It will show you the output.

```text
🔗 Opening browser to authorize...
⚠️ After login, copy the 'code' from the redirected URL 
Paste the 'code' parameter from the URL: <<past your code>>
```

#### Authentication

1. Allow the premission to authenticate.
2. Copy the `code=auth_code` value from newly opened url.
3. Past it inside the terminal.