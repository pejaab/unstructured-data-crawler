from celery import shared_tasks

@shared_task
def scrape(template_id):
	launch_spider.run_spider(template_id)
