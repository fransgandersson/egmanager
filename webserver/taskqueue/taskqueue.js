var celery = require('node-celery');
var celeryClient;

module.exports = TaskQueue;

function TaskQueue()
{
	this.running = false;
	
	this.start = TaskQueue.start;
	this.add = TaskQueue.add;
}

TaskQueue.start = function()
{
	var self = this;
	celeryClient = celery.createClient({CELERY_BROKER_URL: 'amqp://guest:guest@localhost:5672//'});
	celeryClient.on('connect', 
		function() 
		{
			self.running = true;
		});
	celeryClient.on('error', 
		function(err) 
		{	
		    throw err;
		});
};

TaskQueue.add = function(fileName, callback)
{
	if ( !this.running )
	{
		return callback(new Error('not-started'));
	}
	celeryClient.call('tasks.parse_handhistory', [fileName]);
	callback(null);
};