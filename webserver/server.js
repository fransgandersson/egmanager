// *****************************************************************
//					MODULES
// *****************************************************************
var express = require("express");
var events = require('events');
var multer = require('multer');
var path = require('path');
var format = require('util').format;
var mongoClient = require('mongodb').MongoClient;
var celery = require('node-celery');
//*****************************************************************
//				VARIABLES
//*****************************************************************
var sendFileOptions = {root: path.join(__dirname, '/public/')};
var dbConnected = false;
var celeryConnected = false;
var db;

var app=express();
var eventEmitter = new events.EventEmitter();
var hhMulter = multer
	({ 
		dest: './uploads/',
		limits:
		{
			fieldNameSize: 80,
			files: 1,
			fileSize: 600000
		},
		rename: function (fieldname, filename) 
		{
			return filename;
		},
		onFileUploadStart: function (file) 
		{
			console.log('starting upload of ' + file.originalname);
		},
		onFileUploadComplete: function (file, req, res)
		{
			eventEmitter.emit('file-uploaded', file, req, res);
		}
	});

//*****************************************************************
//				API
//*****************************************************************
app.get('/',
	function(req,res)
	{
		res.sendFile('index.html', sendFileOptions);
	});

app.get('/api/upload',
	function(req,res)
	{
		res.sendFile('upload.html', sendFileOptions);
	});

app.get('/api/results',
	function(req,res)
	{
		res.sendFile('todo.html', sendFileOptions);
	});

app.post('/api/upload', hhMulter, 
	function(req,res)
	{
	});
app.listen(80,
	function()
	{
	    console.log('listening on port 80');
	});

//*****************************************************************
//				CONNECT TO DB
//*****************************************************************
mongoClient.connect('mongodb://127.0.0.1:27017/hhQueue', function(err, database) 
{
	if(err) throw err;
	dbConnected = true;
	db = database;
	console.log('connected to mongodb');
});

//*****************************************************************
//				CONNECT TO CELERY
//*****************************************************************
celeryClient = celery.createClient({CELERY_BROKER_URL: 'amqp://guest:guest@localhost:5672//'});
celeryClient.on('connect', 
	function() 
	{
		console.log('celery-connected');
		celeryConnected = true;
	});
celeryClient.on('error', 
	function(err) 
	{	
	    console.log(err);
	    eventEmitter.emit('connection-lost');
	});

//*****************************************************************
//					EVENTS
//  Happy path: 
// 		file-uploaded -> file-validated -> file-stored -> task-queued
// 
//*****************************************************************
// Raised if we lost connection to something. For now immediate exit.
eventEmitter.on('connection-lost', onConnectionLost);
// Raised when a file has been successfully uploaded 
eventEmitter.on('file-uploaded', onFileUploaded);
// Raised when file has been validated
eventEmitter.on('file-validated', onFileValidated);
// Raised when a record has been stored in the db
eventEmitter.on('file-stored', onFileStored);
//Raised when a clery parse task has been queued
eventEmitter.on('task-queued', onTaskQueued);

//*****************************************************************
//					EVENT HANDLERS
//*****************************************************************
function onConnectionLost()
{
	process.exit(1);
}

function onFileUploaded(file, req, res)
{
	console.log('file uploaded');
	var validated = true;
	// TODO: Input validation
			// Filename
			// Size is already checked by multer
			// Maybe some content check 
	if ( dbConnected )
	{
		db.collection('files').findOne({'file': file.name}, 
			function(err, document) 
			{
				if ( document )
				{
					console.log('file already uploaded');
					validated = false;
				}
				if ( err )
				{
					console.log('mongodb error when checking if file already in db');
					validated = false;
				}
			});
	}
	else
	{
		console.log('database not connected');
		fs.unlink(file.path);
		eventEmitter.emit('connection-lost');
		return;
	}
	
	if ( validated )
	{
		eventEmitter.emit('file-validated', file, req, res);
	}
	else
	{
		console.log('invalid file');
		unlink(file.path);
		res.end('Invalid file');
	}
}

function onFileValidated(file, req, res)
{
	if ( dbConnected )
	{
		db.collection('files').insert({ status: 'queued', file: file.name}, {w:1}, function(err) 
		{
			if (err)
			{
				console.warn(err.message);
			}
			else
			{
				console.log('added file to db');
				eventEmitter.emit('file-stored', file.name, req, res);
			}
		});
	}
	else
	{
		console.log('database not connected');
		fs.unlink(file.path);
		eventEmitter.emit('connection-lost');
	}
}
function onFileStored(fileName, req, res)
{
	if ( celeryConnected )
	{
		celeryClient.call('tasks.parse_handhistory', [fileName]);
		console.log('Added file to celery queue');
		eventEmitter.emit('task-queued', fileName, req, res);
	}
	else
	{
		console.log('Celery not connected');
		eventEmitter.emit('connection-lost');
	}
}
function onTaskQueued(fileName, req, res)
{
	res.end('Hand history successfully uploaded!');
}