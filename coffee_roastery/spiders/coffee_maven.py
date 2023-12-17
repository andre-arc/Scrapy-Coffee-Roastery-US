import scrapy


class CoffeeMavenSpider(scrapy.Spider):
    name = 'coffee_maven'
    allowed_domains = ['www.thecoffeemaven.com']
    start_urls = ['http://www.thecoffeemaven.com/roasters']

    def parse(self, response):
        for us_country in response.css('div.roasters-by-state-buttons div.home-roaster'):
            country_name = us_country.css('a.home-roaster-state::text').get()
            country_url = "http://" + self.allowed_domains[0] + us_country.css('a.home-roaster-state::attr(href)').get()

            yield scrapy.Request(url=country_url, callback=self.parse_by_country, meta={
                'country_name': country_name,
                'country_url': country_url,
            })
    
    def parse_by_country(self, response):
        country_name = response.meta.get('country_name')
        country_url = response.meta.get('country_url')

        item = {}
        for roasters in response.css('div.w-dyn-items div.w-dyn-item'):
            item['name'] = roasters.css('.collection-item-link::text').get().strip()
            item['location'] = ', '.join(roasters.css('.category-page-state::text').getall()).strip()
            item['website'] = roasters.css('.info-text::text').get().strip()
            item['phone'] = roasters.css('.collection-item-content-line-3 .info-text::text').get().strip()

            yield {
                'country': country_name,
                'name': item['name'],
                'address': item['location'],
                'website': item['website'],
                'phone': item['phone']
            }

        next_page = response.css('body > div.page-body-section > div > div.w-dyn-list > div.w-pagination-wrapper > a::attr(href)').get()


        # Output next link
        self.log(f"find next link : {next_page}")

        if next_page is not None:
            yield scrapy.Request(url=country_url + next_page, callback=self.parse_by_country, meta={
                'country_name': country_name,
                'country_url': country_url,
            })

