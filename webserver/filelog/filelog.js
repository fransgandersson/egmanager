var mongoClient = require('mongodb').MongoClient;
var db;

module.exports = FileLog;

function FileLog(name)
{
	this.name = name;
	this.running = false;

	this.start = FileLog.start;
	this.get = FileLog.get;
	this.add = FileLog.add;
	
}

FileLog.start = function()
{
	var self = this;

	//	connect to db
	mongoClient.connect('mongodb://127.0.0.1:27017/fileLog', 
		function(err, database) 
		{
			if(err) throw err;
			self.running = true;
			db = database;
		});
};
FileLog.get = function (fileName, callback)
{
	if ( !this.running )
	{
		return callback(new Error('not-started'));
	}
	db.collection(this.name).findOne({'file': fileName}, 
		function(err, document) 
		{
			if ( err )
			{
				return callback(err);
			}
			return callback(null, document);
		});
};
FileLog.add = function (fileName, callback)
{
	if ( !this.running )
	{
		return callback(new Error('not-started'));
	}
	db.collection(this.name).insert({ status: 'queued', file: fileName}, {w:1}, 
		function(err) 
		{
			if (err)
			{
				return callback(err);
			}
			else
			{
				return callback(null);
			}
		});
};

