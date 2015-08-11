from __future__ import absolute_import

from celery import shared_task
from interface.crawler.crawler.launch_spider import run_spider

@shared_task
def scrape(template_id):
	run_spider(template_id)
