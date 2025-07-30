### Create `/articles` folder 

```sh
cd artical-generator
mkdir articles
```

### Create `.env` file to store the enviroment variables.

```sh
CLIENT_ID = your_wordpress_client_id
CLIENT_SECRET = your_wordpress_client_secret
GEMINI_API_KEY = gemini_api_key
```

### Geting the wordpress credentials
1. Go to https://developer.wordpress.com/apps/ 
2. Create new app or select the existing one.
3. You will get the `client_id` and `client_secret`
4. copy and past it inside `.env` variables


### Getting the Gemini API Key
1. Go to the https://aistudio.google.com/app/apikey
2. Click on the `Create Api Key`.
3. Copy the key and past it inside the `.env`


### Run the program.
```sh
python main.py
```

### Authenticating with wordpress rest api

1. When you run the program allow the premission.
2. Copy the code value from newly opened url.
3. Past it inside the terminal.