from playwright.sync_api import sync_playwright
import time
import csv

def nba_scrape():
    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.actionnetwork.com/nba/odds")
        
        page.wait_for_selector("div[data-testid='odds-tools-sub-nav__odds-type']")
        dropdown = page.query_selector("div[data-testid='odds-tools-sub-nav__odds-type'] > select")
        
        categories = ['spread', 'total', 'ml']
        final_odds_data = []
        
        game_data = {}

        for category in categories:
            dropdown.select_option(value=category)
            time.sleep(3)
            
            
            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(1)
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)
            
            
            page.wait_for_selector("table[class='css-1uek3nh e1ujzcpo0']")
            odds_table = page.query_selector_all("table[class='css-1uek3nh e1ujzcpo0'] > tbody > tr")
            
            for row in odds_table:
                try:
                    
                    teams = row.query_selector_all("a[class='css-1wjesfo eek0sah0'] .game-info__teams .game-info__team-info .game-info__team--desktop span")
                    if len(teams) >= 2:
                        away_team = teams[0].inner_text().strip()
                        home_team = teams[1].inner_text().strip()
                    else:
                        continue

                    
                    game_key = (home_team, away_team)
                    if game_key not in game_data:
                        game_data[game_key] = {
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_spread": None,
                            "away_spread": None,
                            "over": None,
                            "under": None,
                            "away_moneyline": None,
                            "home_moneyline": None
                        }

                    
                    odds = row.query_selector_all(".best-odds__odds-container .css-1vdqu87 .book-cell__odds .css-1qynun2.ep4ea6p2")
                    
                    if category == 'spread':
                        if len(odds) >= 2:
                            away_spread = odds[0].inner_text().strip()
                            home_spread = odds[1].inner_text().strip()
                            game_data[game_key]["away_spread"] = away_spread
                            game_data[game_key]["home_spread"] = home_spread
                    
                    elif category == 'total':
                        if len(odds) >= 4:
                            over = odds[2].inner_text().strip()
                            under = odds[3].inner_text().strip()
                            game_data[game_key]["over"] = over
                            game_data[game_key]["under"] = under
                    
                    elif category == 'ml':
                        if len(odds) >= 6:
                            away_moneyline = odds[4].inner_text().strip()
                            home_moneyline = odds[5].inner_text().strip()
                            game_data[game_key]["away_moneyline"] = away_moneyline
                            game_data[game_key]["home_moneyline"] = home_moneyline

                except Exception as e:
                    print(f"Error scraping row: {e}")
        
        
        final_odds_data = list(game_data.values())
        
        browser.close()
        return final_odds_data


def write_to_csv(data):
    keys = data[0].keys()
    with open('NBAgame_lines_of_the_day.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


nba_odds = nba_scrape()

if nba_odds:
    write_to_csv(nba_odds)
    print("Data has been written to NBAgame_lines_of_the_day.csv.")
else:
    print("No valid data to write.")
