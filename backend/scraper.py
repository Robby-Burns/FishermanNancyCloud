import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict
from datetime import datetime


class CanneryScraper:
    """Scrape cannery websites for current fish prices"""

    def __init__(self):
        self.timeout = 10.0

    async def scrape_westport_cannery(self, url: str) -> Optional[Dict[str, float]]:
        """
        Scrape Westport cannery website for prices.
        
        Returns:
            {
                "Crab": 5.50,
                "Salmon": 4.20,
                "Halibut": 4.80
            }
            or None if scraping fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # This is a placeholder - actual scraping logic depends on the website structure
            # Common patterns:
            # - <table> with fish types and prices
            # - <div class="price"> elements
            # - JSON data in <script> tags

            prices = {}

            # Example: Look for table with prices
            # Adjust selectors based on actual website
            price_table = soup.find('table', class_='prices')
            if price_table:
                rows = price_table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        fish_type = cols[0].text.strip()
                        price_text = cols[1].text.strip()
                        # Extract number from price text like "$4.20/lb"
                        price = self._extract_price(price_text)
                        if price:
                            prices[fish_type] = price

            # Example: Look for div elements
            price_divs = soup.find_all('div', class_='fish-price')
            for div in price_divs:
                fish_type = div.find('span', class_='fish-name')
                price_elem = div.find('span', class_='price')
                if fish_type and price_elem:
                    fish = fish_type.text.strip()
                    price = self._extract_price(price_elem.text.strip())
                    if price:
                        prices[fish] = price

            return prices if prices else None

        except Exception as e:
            print(f"Error scraping cannery: {e}")
            return None

    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract price from text like "$4.20/lb" or "4.20"
        """
        try:
            # Remove common characters
            clean = price_text.replace('$', '').replace('/lb', '').replace(' ', '')
            return float(clean)
        except (ValueError, AttributeError):
            return None

    async def scrape_generic_cannery(self, url: str) -> Optional[Dict[str, float]]:
        """
        Generic scraper - attempts common patterns.
        More robust but less accurate than site-specific scrapers.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for common fish names and nearby prices
            fish_keywords = ['crab', 'salmon', 'halibut', 'cod', 'tuna']
            prices = {}

            text = soup.get_text()
            lines = text.split('\n')

            for i, line in enumerate(lines):
                line_lower = line.lower()
                for fish in fish_keywords:
                    if fish in line_lower:
                        # Look for price in current line or next few lines
                        for j in range(i, min(i + 3, len(lines))):
                            price = self._extract_price(lines[j])
                            if price:
                                fish_capitalized = fish.capitalize()
                                prices[fish_capitalized] = price
                                break

            return prices if prices else None

        except Exception as e:
            print(f"Error scraping cannery: {e}")
            return None

    async def test_scraper(self, url: str) -> Dict[str, any]:
        """
        Test scraper on a URL and return diagnostic info.
        Useful for debugging when adding a new cannery.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Return diagnostic info
            return {
                "success": True,
                "status_code": response.status_code,
                "title": soup.title.string if soup.title else None,
                "tables_found": len(soup.find_all('table')),
                "divs_with_price_class": len(soup.find_all('div', class_=lambda x: x and 'price' in x.lower())),
                "sample_text": soup.get_text()[:500],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
