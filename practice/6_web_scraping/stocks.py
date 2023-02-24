from bs4 import BeautifulSoup
import re
import requests
import pandas as pd

BASE_URL = "https://finance.yahoo.com"
MOST_ACTIVE = f"{BASE_URL}/most-active"
HEADERS = {"User-Agent": "Mozilla/5.0"}
SUMMARY = {"/profile?p="}
BLACK_ROCK = "BLK"


class CeoParser:

    def __init__(self):
        self.columns = None
        self.extracted_page = None
        self.stock_query_list = []
        self.summary_links = []
        self.statistics_links = []
        self.profile_links = []
        self.ceo_list = []
        self.change_list = []
        self.all_br_holders = []

    @staticmethod
    def check_page_valid(url):
        """Check if the page returns an error"""
        response = requests.get(url, headers=HEADERS)
        if not response.ok:
            print('Status code:', response.status_code)
            raise Exception(f'Failed to load page {url}')
        return response

    def get_page(self, url):
        """Download a webpage and return a beautifulsoup doc"""
        response = self.check_page_valid(url)
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup

    @staticmethod
    def total_stock_num(soup) -> str:
        """Parse the most_active page for total number of stocks and return a string"""
        total_stock = soup.find("span", class_="Mstart(15px) Fw(500) Fz(s)").text.split(" ")[2]
        print(f"Number of all stocks: {total_stock}")
        return total_stock

    @staticmethod
    def query_stock_num(stock_amount):
        """Create query with either total number of stocks or custom value and return a string"""
        full_query = f"{MOST_ACTIVE}?count={stock_amount}"
        return full_query

    def get_company_query(self, soup):
        """Extract the query for each stock and return a list of strings"""
        rows = soup.find('tbody').find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            self.stock_query_list.append(columns[0].find("a")["href"])
        return self.stock_query_list

    def link_summary(self):
        """Use extracted stock queries to create full stock summary links and return a list of strings"""
        for href in self.stock_query_list:
            self.summary_links.append(f"{BASE_URL}{href.split('?')[0]}")
        return self.summary_links

    def link_tab(self):
        """Create full stock tab links and return a list of strings"""
        for summary in self.summary_links:
            profile_link = f"{summary}/profile?p={summary[summary.rfind('/') + 1:]}"
            statistics_link = f"{summary}/key-statistics?p={summary[summary.rfind('/') + 1:]}"
            self.profile_links.append(profile_link)
            self.statistics_links.append(statistics_link)
        return self.profile_links, self.statistics_links

    def goto_blackrock(self):
        holder_url = f"{BASE_URL}/quote/{BLACK_ROCK}/holders?p={BLACK_ROCK}"
        br_holders = self.get_page(holder_url)
        return br_holders

    def get_top_holders(self):
        holder_page = self.goto_blackrock()
        holder_table = holder_page.find('h3', text='Top Institutional Holders').find_next_sibling('table').find('tbody')
        labels = ["Name", "Shares", "Date Reported", "% Out", "Value"]
        for row in holder_table:
            holder_value = row.find_all('td')
            values = []
            for value in holder_value:
                values.append(value.text)
            holders_dict = dict(zip(labels, values))
            self.all_br_holders.append(holders_dict)
        return self.all_br_holders

    def extract_ceo(self):
        for link in self.profile_links:
            self.extracted_page = self.get_page(link)
            rows = self.extracted_page.find('tbody').find_all("tr")
            for row in rows[:3]:
                self.columns = row.find_all("td")
                re_ceo = re.search(r"C[.]?E[.]?O[.]?", self.columns[1].text)
                if re_ceo:
                    if self.get_ceo_data() is not None:
                        self.ceo_list.append(self.get_ceo_data())
        return self.ceo_list

    def extract_change_values(self):
        for link in self.statistics_links:
            change_dict = {"Name": "", "Code": "", "52-Week Change": 0, "Total cash": ""}
            self.extracted_page = self.get_page(link)
            name = self.extracted_page.find('h1', class_='D(ib) Fz(18px)').text.split('(')[0][:-1]
            code = self.extracted_page.find('h1', class_='D(ib) Fz(18px)').text.split('(')[1][:-1]
            change_dict['Name'], change_dict['Code'] = name, code

            ch_table = self.extracted_page.find('h3', text='Stock Price History').find_next_sibling('table')
            ch_row = ch_table.find_all('tr')[1]
            ch_value = ch_row.find_all('td')[1].text[:-1]
            change_dict['52-Week Change'] = float(ch_value)

            bal_table = self.extracted_page.find('h3', text='Balance Sheet').find_next_sibling('table')
            cash_row = bal_table.find('tr')
            cash_value = cash_row.find_all('td')[1].text
            change_dict['Total cash'] = cash_value
            self.change_list.append(change_dict)

        return self.change_list

    def get_ceo_data(self):
        ceo_dict = {"Name": "", "Code": "", "Country": "", "Employees": 0, 'CEO name': self.columns[0].text,
                    'CEO Year Born': 0}
        if self.columns[4].text != "N/A":
            ceo_dict['CEO Year Born'] = int(self.columns[4].text)
        else:
            return None

        address = self.extracted_page.find('p', class_="D(ib) W(47.727%) Pend(40px)")
        for br in address.find_all("br"):
            br.replace_with("\n")
        country = address.text.splitlines()[-3]
        ceo_dict["Country"] = country
        name = self.extracted_page.find('h1', class_='D(ib) Fz(18px)').text.split('(')[0][:-1]
        ceo_dict["Name"] = name
        code = self.extracted_page.find('h1', class_='D(ib) Fz(18px)').text.split('(')[1][:-1]
        ceo_dict["Code"] = code
        emp_section = self.extracted_page.find('p', class_="D(ib) Va(t)")
        emp_info = emp_section.find('span', text="Full Time Employees").find_next('span').text
        ceo_dict["Employees"] = emp_info
        return ceo_dict

    def find_youngest(self):
        ceos_sorted = sorted(self.ceo_list, key=lambda d: d['CEO Year Born'], reverse=True)
        youngest_ceos = ceos_sorted[:5]
        return youngest_ceos

    def find_best_change(self):
        change_sorted = sorted(self.change_list, key=lambda d: d['52-Week Change'], reverse=True)
        best_change = change_sorted[:10]
        return best_change

    # def results_to_csv(self):
    #     result_dicts = [self.find_youngest(), self.find_best_change(), self.get_top_holders()]
    #     with open('parsing_results.csv', 'w', newline='') as csvfile:
    #         for results in result_dicts:
    #             writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
    #             writer.writeheader()
    #             for entry in results:
    #                 writer.writerow(entry)

    def results_to_sheet(self):
        result_dicts = [self.find_youngest(), self.find_best_change(), self.get_top_holders()]
        separators = [
            "=================================== 5 stocks with most youngest CEOs ===================================",
            "================================== 10 stocks with best 52-Week Change ==================================",
            "================================ 10 biggest BlackRock Inc. Shareholders ================================"
        ]
        i = 0

        for result in result_dicts:
            print(separators[i])
            df = pd.DataFrame.from_records(result)
            print(df.to_string(index=False, justify="left"))
            i += 1


page = CeoParser()

query = page.get_page(MOST_ACTIVE)
total_stock_num = page.total_stock_num(query)
full_query = page.query_stock_num(15)
full_page = page.get_page(full_query)
stock_href = page.get_company_query(full_page)
link_summary = page.link_summary()

# ceo and change
link_profiles, link_statistics = page.link_tab()
page.extract_change_values()
page.extract_ceo()
# blackrock
page.get_top_holders()

page.results_to_sheet()
