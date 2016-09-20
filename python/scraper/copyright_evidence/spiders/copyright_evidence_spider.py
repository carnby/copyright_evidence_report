from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from copyright_evidence.items import GenericPage
import urlparse
import string
import logging
from copyright_evidence.spiders import util

class CopyrightEvidenceSpider(CrawlSpider):
    name = 'copyright_evidence_spider'
    allowed_domains = ['www.copyrightevidence.org']
    start_urls = 'http://www.copyrightevidence.org/evidence-wiki/index.php?title=Special:AllPages',
    rules = [
        # Follow all 'All Pages' navigational links.
        Rule(
            link_extractor = LxmlLinkExtractor(
                allow = '/evidence-wiki/index\.php\?title=Special:AllPages&from=.*$',
                restrict_xpaths='//*[@id="mw-content-text"]/div[@class="mw-allpages-nav"]')),
        # Follow all page links from the 'All pages' page.
        Rule(
            link_extractor = LxmlLinkExtractor(
                allow = '/evidence-wiki/index\.php/',
                restrict_xpaths='//*[@id="mw-content-text"]/ul[@class="mw-allpages-chunk"]/li'),
            # From each page, follow the 'View source' link.
            # And process the page
            callback = 'goto_edit_source',
            follow = False),
    ]

    def goto_edit_source(self, response):
        # Add ?action=edit to the URL of the page and
        # return a new request with parse_page as callback.
        yield Request(
            response.url + '?action=edit',
            callback = self.parse_page)

    def parse_page(self, response):
        sel = Selector(response)
        url = response.url

        # Check if the 'Permission error' message appears.
        if sel.xpath('//*[@id="firstHeading"]/text()').extract()[0] == 'Permission error':
            logging.error('Permission error.')
            return

        textarea = sel.xpath('//textarea/text()')
        mediawiki_text = textarea.extract()[0]
        parsed_text, templates = util.parse_templates_from_text(mediawiki_text)
        item = util.parse_item_from_templates(templates)
        if item is None:
            if len(parsed_text) == 0:
                return
            item = GenericPage()
        item['url'] = url.replace('?action=edit', '')
        item['item_type'] = str(type(item))
        item['page_title'] = sel.xpath('//*[@id="contentSub"]/a/text()').extract()[0]
        if len(parsed_text) != 0:
            item['text'] = parsed_text
        yield item
