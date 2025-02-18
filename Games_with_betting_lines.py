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

        
        combined_data = {
            "home_team": None,
            "away_team": None,
            "home_spread": None,
            "away_spread": None,
            "over": None,
            "under": None,
            "away_moneyline": None,
            "home_moneyline": None
        }

        for category in categories:
            
            dropdown.select_option(value=category)
            
            
            time.sleep(3)

            
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
                    
                    
                    if combined_data["home_team"] is None:
                        combined_data["home_team"] = home_team
                    if combined_data["away_team"] is None:
                        combined_data["away_team"] = away_team
                    
                    
                    odds = row.query_selector_all(".best-odds__odds-container .css-1vdqu87 .book-cell__odds .css-1qynun2.ep4ea6p2")
                    
                    
                    if category == 'spread':
                        if len(odds) >= 2:
                            away_spread = odds[0].inner_text().strip()
                            home_spread = odds[1].inner_text().strip()
                        else:
                            continue

                        combined_data["home_spread"] = home_spread
                        combined_data["away_spread"] = away_spread

                    elif category == 'total':
                        if len(odds) >= 4:
                            over = odds[2].inner_text().strip()
                            under = odds[3].inner_text().strip()
                        else:
                            continue

                        combined_data["over"] = over
                        combined_data["under"] = under

                    elif category == 'ml':
                        if len(odds) >= 6:
                            away_moneyline = odds[4].inner_text().strip()
                            home_moneyline = odds[5].inner_text().strip()
                        else:
                            continue

                        combined_data["away_moneyline"] = away_moneyline
                        combined_data["home_moneyline"] = home_moneyline

                except Exception as e:
                    print(f"Error scraping row: {e}")

        
        final_odds_data.append(combined_data)

        
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
