var mongoClient = require('mongodb').MongoClient;
var db;

module.exports = FileLog;

function FileLog(name, options)
{
	this.name = name;
	this.running = false;
	this.log = options.log.child({module: 'fileLog'});

	this.start = FileLog.start;
	this.get = FileLog.get;
	this.add = FileLog.add;
	this.getRecent = FileLog.getRecent;
}

FileLog.start = function()
{
	var self = this;

	//	connect to db
	mongoClient.connect('mongodb://127.0.0.1:27017/fileLog', 
		function(err, database) 
		{
			if(err)
			{
				self.log.error('db connection failed: ' + err.message);
			}
			self.running = true;
			db = database;
			self.log.info('started');
		});
};
FileLog.get = function (fileName, callback)
{
	var self = this;
	
	if ( !this.running )
	{
		this.log.error('db not connected');
		return callback(new Error('not-started'));
	}
	db.collection(this.name).findOne({'file': fileName}, 
		function(err, document) 
		{
			if ( err )
			{
				self.log.error('get: ' + err.message);
				return callback(err);
			}
			return callback(null, document);
		});
};
FileLog.add = function (fileName, callback)
{
	var self = this;
	
	if ( !this.running )
	{
		this.log.error('db not connected');
		return callback(new Error('not-started'));
	}
	db.collection(this.name).insert({ status: 'queued', file: fileName, time: Date.now()}, {w:1}, 
		function(err) 
		{
			if (err)
			{
				self.log.error('add: ' + err.message);
				return callback(err);
			}
			else
			{
				return callback(null);
			}
		});
};

FileLog.getRecent = function (count, callback)
{
	var self = this;
	
	if ( !this.running )
	{
		this.log.error('db not connected');
		return callback(new Error('not-started'));
	}
	db.collection(this.name).find({}, {'limit': count, 'sort': {time: -1}},
		function(err, cursor) 
		{
			if ( err )
			{
				self.log.error('getRecent: ' + err.message);
				return callback(err);
			}
			cursor.toArray(callback);
		});
};