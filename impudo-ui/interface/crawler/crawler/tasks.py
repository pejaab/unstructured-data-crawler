from celery import Celery
import launch_spider

app = Celery('tasks', backend='rpc://', broker='amqp://')
#Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def scrape(template_id):
	launch_spider.run_spider(template_id)

