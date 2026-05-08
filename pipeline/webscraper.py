import requests, random
from bs4 import BeautifulSoup
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

class HackerNewsScraper:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EthicalScraper/1.0"
        }
        self.rp = RobotFileParser()
        self.rp.set_url(urljoin(self.base_url, "robots.txt"))
        self.rp.read()

    def _can_fetch(self, url):
        """Checks robots.txt permissions."""
        return self.rp.can_fetch(self.headers["User-Agent"], url)

    def _get_soup(self, url, max_retries=3):
        """Fetches URL and returns a BeautifulSoup object with error handling."""
        if not self._can_fetch(url):
            print(f"[!] Access denied by robots.txt for: {url}")
            return None

        retries = 0
        backoff_time = 5

        while retries < max_retries:
            try:
                jitter = random.uniform(0.5, 1.5)
                time.sleep(backoff_time + jitter)  # Respectful delay

                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 429:
                    retries += 1
                    backoff_time *= 2
                    print(f"[!] 429 Client Error. Retrying in {backoff_time}s... (Attempt {retries}/{max_retries})")
                    continue

                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')

            except requests.exceptions.RequestException as e:
                print(f"[!] Connection error: {e}")
                retries += 1
                time.sleep(backoff_time)

        print(f"[!!!] Failed to fetch {url} after {max_retries} attempts.")
        return None

    def _extract_thread_data(self, titles, subtext, limit=10):
        """Parses the main list rows to extract thread metadata."""
        threads = []
        # HN uses two rows per story: 'athing' for title/id, and the following 'td' for metadata
        for i in range(0, len(titles)):
            if len(threads) >= limit:
                break

            try:
                story_row = titles[i]
                meta_row = subtext[i]

                title_tag = story_row.select_one(".titleline > a")
                score_tag = meta_row.select_one(".score")
                # Comments are usually the last link in the subtext
                links = meta_row.select(".subline > a")
                comment_tag = [l for l in links if "comment" in l.text]

                thread_id = story_row.get("id")
                points = int(score_tag.text.split()[0]) if score_tag else 0
                comment_count = int(comment_tag[0].text.split('\xa0')[0]) if comment_tag else 0

                threads.append({
                    "id": thread_id,
                    "title": title_tag.text,
                    "link": title_tag["href"],
                    "points": points,
                    "comments_count": comment_count,
                    "item_url": urljoin(self.base_url, f"item?id={thread_id}"),
                    "top_comments": []
                })
            except (AttributeError, IndexError):
                continue
        return threads

    def get_comments(self, thread):
        """Navigates to item page and scrapes the first 5 top-level comments."""
        soup = self._get_soup(thread["item_url"])
        if not soup:
            return

        # Find all comment rows
        comment_rows = soup.select("tr.comtr")
        top_level_comments = []

        for row in comment_rows:
            if len(top_level_comments) >= 5:
                break

            # Identify depth: top-level comments have an indent image with width="0"
            indent_img = row.select_one("td.ind > img")
            if indent_img and indent_img.get("width") == "0":
                comm_text_part = row.select_one(".commtext")
                if comm_text_part:
                    # Clean up text (remove 'reply' links often included in selection)
                    for reply_link in comm_text_part.select(".reply"):
                        reply_link.decompose()
                    top_level_comments.append(comm_text_part.get_text(strip=True))

        thread["top_comments"] = top_level_comments

    def scrape_categories(self):
        """Main execution flow for all categories."""
        results = {}

        # 1. Front Page (for Top Points and Top Comments)
        print("[*] Processing Front Page...")
        front_soup = self._get_soup(self.base_url)
        if front_soup:
            all_threads = self._extract_thread_data(front_soup.select(".athing"), front_soup.select(".subtext"), limit=30)
            results["Top 10 by Points"] = sorted(all_threads, key=lambda x: x['points'], reverse=True)[:10]
            results["Top 10 by Comments"] = sorted(all_threads, key=lambda x: x['comments_count'], reverse=True)[:10]

        # 2. Newest Page
        print("[*] Processing Newest Page...")
        new_soup = self._get_soup(urljoin(self.base_url, "newest"))
        if new_soup:
            results["Top 10 Newest"] = self._extract_thread_data(new_soup.select(".athing"), new_soup.select(".subtext"), limit=10)

        # 3. Enrich with Comments
        for category, threads in results.items():
            print(f"[*] Fetching comments for {category}...")
            for thread in threads:
                self.get_comments(thread)

        return results

    def display_results(self, data):
        """Prints the structured data to the console."""
        for category, threads in data.items():
            print(f"\n{'=' * 60}")
            print(f" CATEGORY: {category}")
            print(f"{'=' * 60}")

            for t in threads:
                print(f"\n    Title: {t['title']}")
                print(f"    Link: {t['link']}")
                print(f"    Stats: {t['points']} points | {t['comments_count']} comments")
                print("    Top Comments:")
                if not t['top_comments']:
                    print("      (No top-level comments found)")
                for i, comm in enumerate(t['top_comments'], 1):
                    # Truncate long comments for cleaner console output
                    clean_comm = (comm[:120] + '...') if len(comm) > 120 else comm
                    print(f"      {i}. {clean_comm}")