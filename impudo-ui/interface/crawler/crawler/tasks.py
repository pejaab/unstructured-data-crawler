from celery import Celery

app = Celery('tasks', backend='rpc://', broker='amqp://')
#Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
	return x+y

