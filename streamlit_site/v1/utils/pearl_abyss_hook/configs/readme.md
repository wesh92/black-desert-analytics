# About secrets_cookes.py

This file is required for the `pa_base_item_info.py` to work. Below is the format.

```python
cookies = {
    "visid_incap_2512188": "",
    "blackdesert_cid": "",
    "visitTopicNoList": "",
    "visid_incap_2504207": "",
    "lang": "en-US",
    "visid_incap_2504216": "",
    "visid_incap_2504212": "",
    "nlbi_2512188": "",
    "incap_ses_78_2512188": "",
    "naeu.Session": "",
    "bodyCountryCode": "us",
    "rating": "PEGI",
    "nlbi_2512188_2147483392": "",
    "TradeAuth_Session_EU": "",
    "nlbi_2504216": "",
    "incap_ses_78_2504216": "",
    "nlbi_2504212": "",
    "incap_ses_78_2504212": "",
    "TradeAuth_Session": "",
    "__RequestVerificationToken": "",
    "tradeHistory": "",
}

request_token = ""
```

You can get `request_token` by going to your local PA Trade Website, hitting F12, navigating to "Network" then "Fetch/XHR" and then clicking "Payload".
It is the field titled "`__RequestVerificationToken`".

For the cookies it is a bit more involved. I recommend going to the same place as above, but right-clicking the `GetWorldMarketList` request, hitting "Copy" and then "Copy as cURL (bash)". You can see the entire cookie string in there as one of the headers. You can either parse it manually or create a convenice script to do it for you.

The below script is **untested**:

```python
# Given cURL cookie string
cookie_str = ()

# Split the string by '; ' to get individual cookies and then by '=' to separate names and values
cookie_pairs = [pair.split('=') for pair in cookie_str.split('; ')]

# Create a dictionary from the pairs
cookie_dict = {pair[0]: pair[1] for pair in cookie_pairs}

# Update the provided cookies dictionary with the values from cookie_dict
cookies = {
    "visid_incap_2512188": "",
    "blackdesert_cid": "",
    "visitTopicNoList": "",
    "visid_incap_2504207": "",
    "lang": "en-US",
    "visid_incap_2504216": "",
    "visid_incap_2504212": "",
    "nlbi_2512188": "",
    "incap_ses_78_2512188": "",
    "naeu.Session": "",
    "bodyCountryCode": "us",
    "rating": "PEGI",
    "nlbi_2512188_2147483392": "",
    "TradeAuth_Session_EU": "",
    "nlbi_2504216": "",
    "incap_ses_78_2504216": "",
    "nlbi_2504212": "",
    "incap_ses_78_2504212": "",
    "TradeAuth_Session": "",
    "__RequestVerificationToken": "",
    "tradeHistory": "",
}
cookies.update(cookie_dict)
cookies
```

Happy Scraping!
