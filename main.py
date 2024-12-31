import json
import re
import cloudscraper

class HypixelRewardClaimer:
    def __init__(self, url: str, option: int = 0):
        self.url = url
        self.default_option = option
        self.scraper = cloudscraper.create_scraper()
        self.cookies = None
        self.headers = None

    def claim_reward(self, option: int = None):
        if option is None:
            option = self.default_option

        response = self.scraper.get(self.url)
        self.cookies = response.cookies
        self.headers = response.headers
        
        headers_str = "\n".join(f"{key}: {value}" for key, value in self.headers.items())
        csrf_match = re.search(r"_csrf=([a-zA-Z0-9]+)", headers_str)

        if not csrf_match:
            raise ValueError("No _csrf token found in the headers!")
        
        csrf_token = csrf_match.group(1)
    
        html_content = response.text
        
        security_token_match = re.search(r'window\.securityToken\s*=\s*"([^"]+)"', html_content)
        if not security_token_match:
            raise ValueError("No securityToken found in the HTML!")
        security_token = security_token_match.group(1)
        
        app_data_match = re.search(r'window\.appData\s*=\s*\'([^\']+)\'', html_content)
        if not app_data_match:
            raise ValueError("No appData found in the HTML!")
        app_data = app_data_match.group(1)
        
        data = json.loads(app_data)
        
        reward_id = data.get("id")
        daily_streak = data.get("dailyStreak", {})
        daily_streak_value = daily_streak.get("value")
        daily_streak_high_score = daily_streak.get("highScore")
        active_ad = data.get("activeAd")
        
        print("Reward ID:", reward_id)
        print("Current Daily Streak:", daily_streak_value)
        print("High Score:", daily_streak_high_score)

        post_headers = {
            "_csrf=": csrf_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        
        claim_url = (
            "https://rewards.hypixel.net/claim-reward/claim"
            f"?id={reward_id}&option={option}"
            f"&activeAd={active_ad}&_csrf={security_token}"
        )
        
        post_response = self.scraper.post(claim_url, headers=post_headers, cookies=self.cookies)
        
        print("Status Code:", post_response.status_code)
        print("Response Text:", post_response.text)
        
        return post_response


if __name__ == "__main__":
    url = "https://rewards.hypixel.net/claim-reward/bbd6dfb4"
    claimer = HypixelRewardClaimer(url=url, option=1)
    response = claimer.claim_reward()
