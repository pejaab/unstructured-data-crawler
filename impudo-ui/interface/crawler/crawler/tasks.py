from celery import Celery
from launch_spider import CrawlerScript

app = Celery('tasks', backend='rpc://', broker='amqp://')
#Celery('tasks', broker='amqp://guest@localhost//')

'''@app.task
def add(x, y):
	return x+y'''

@app.task
def scrape():
	c=CrawlerScript()
	c.run_spider()

