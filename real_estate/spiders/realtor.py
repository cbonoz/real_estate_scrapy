# -*- coding: utf-8 -*-
import scrapy
OUTPUT_FILE = 'sea_realtor_scrape.tsv'

# Instance of a Sold House.
class House:
    HEADER = 'address\tzip\tprice\tsell_date\tsq_feet\tbeds\tbaths'

    def convert_list_to_str(self, items):
        text = ''.join(items)
        text = text.strip().rstrip('\n')
        return text

    def parse_comma_int(self, x):
        try:
            x = str(x).replace(',', '')
            return int(x)
        except Exception as e:
            return ''


    def parse_address_from_body(self, body):
        addr = body.xpath('//span[contains(@class, "listing-street-address")]//text()').extract()
        addr += [','] + body.xpath('//span[contains(@class, "listing-city")]//text()').extract()
        addr += [','] + body.xpath('//span[contains(@class, "listing-region")]//text()').extract()
        return addr

    def __str__(self):
        return ('%s\t%s\t%s\t%s\t%s\t%s\t%s' 
        % (self.address, self.zip, self.price, self.sell_date, self.sqft, self.beds, self.baths))

    def __init__(self, body=None):
        # body is the srp_body response.
        self.address = self.parse_address_from_body(body)
        self.price = body.xpath('//div[contains(@class, "srp-item-price")]//text()').extract()
        self.zip = body.xpath('//span[contains(@class, "listing-postal")]//text()').extract()
        self.sell_date = body.xpath('//span[contains(@class, "srp-item-price-helper")]//text()').extract()
        self.beds = body.xpath('//li[contains(@data-label, "property-meta-beds")]//span[contains(@class, "data-value")]//text()').extract()
        self.baths = body.xpath('//li[contains(@data-label, "property-meta-baths")]//span[contains(@class, "data-value")]//text()').extract()
        self.sqft = body.xpath('//li[contains(@data-label, "property-meta-sqft")]//span[contains(@class, "data-value")]//text()').extract()

        self.address = self.convert_list_to_str(self.address)
        self.price = self.convert_list_to_str(self.price[0]) # Select only the price field.
        self.currency = self.price[0]
        self.price = self.parse_comma_int(self.price[1:])
        self.zip = int(self.convert_list_to_str(self.zip))
        self.sell_date = self.convert_list_to_str(self.sell_date[2:]) # Remove the 'On ' from the string list.
        self.beds = self.convert_list_to_str(self.beds)
        self.baths = self.convert_list_to_str(self.baths)
        self.sqft = self.parse_comma_int(self.convert_list_to_str(self.sqft))   

# Main Realtor Spider class
class RealtorSpider(scrapy.Spider):
    name = "realtor_spider"
    allowed_domains = ["realtor.com"]
    MAX_PAGE = 5
    # start_urls = ['http://realtor.com/']

    def make_realtor_url(self, city, state, page):
        url = 'http://www.realtor.com/soldhomeprices/%s_%s/pg-%d?pgsz=50' % (city, state, page)
        return url

    def start_requests(self):
        city = "Seattle"
        state = 'WA'
        urls = [self.make_realtor_url(city.replace(" ", ""), state, i)
                for i in range(1, RealtorSpider.MAX_PAGE)]
        with open(OUTPUT_FILE, 'w') as f:
            f.write(House.HEADER + "\n")
        for i, url in enumerate(urls):
            print('Page %d' % i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        house_prices = response.xpath('//div[contains(@class, "srp-item-body")]').extract()
        print('Found %d prices' % len(house_prices))
        with open(OUTPUT_FILE, 'a') as f:
            for p in house_prices:
                sel = scrapy.Selector(text=p, type="html")
                house = House(sel)
                print(house.__dict__)
                f.write("%s\n" % house)
      
