import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import RredriverbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class RredriverbankSpider(scrapy.Spider):
	name = 'redriverbank'
	start_urls = ['https://www.redriverbank.net/media-relations/']

	def parse(self, response):
		articles = response.xpath('//section[@class="archive content-block"]/ul/li')
		for article in articles:
			date = article.xpath('.//span/text()').get()
			post_links = article.xpath('.//a/@href').get()
			if not 'pdf' in post_links:
				yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="field__item"]/text() |//h1/text()').get()
		content = response.xpath('//div[@class="node__content"]//text()[not (ancestor::span[@class="file file--mime-application-pdf file--application-pdf"])] | //div[@class="content-block"]//text()[not (ancestor::a[@class="btn btn-primary"] or ancestor::aside)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=RredriverbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
