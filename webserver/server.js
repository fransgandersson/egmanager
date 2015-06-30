// *****************************************************************
//					MODULES
// *****************************************************************
var express = require("express");
var events = require('events');
var multer = require('multer');
var fs = require('fs');
var path = require('path');
var fileLog = require('./filelog/filelog.js');
var taskQueue = require('./taskqueue/taskqueue.js');

//*****************************************************************
//				VARIABLES
//*****************************************************************
var sendFileOptions = {root: path.join(__dirname, '/public/')};

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

app.get('/api/uploads',
	function(req,res)
	{
		res.sendFile('upload.html', sendFileOptions);
	});

app.get('/api/results',
	function(req,res)
	{
		res.sendFile('todo.html', sendFileOptions);
	});

app.post('/api/uploads', hhMulter, 
	function(req,res)
	{
	});
app.listen(80,
	function()
	{
	    console.log('listening on port 80');
	});


//*****************************************************************
//				START MODULES
//*****************************************************************
var fileLogClient = new fileLog('uploaded-files');
fileLogClient.start();
var taskQueueClient = new taskQueue();
taskQueueClient.start();

//*****************************************************************
//					EVENTS
//  Paths: 
// 		uploaded ->	validated ->	not-duplicate ->	logged ->	task-queued
//						|				|
//						v				v
//					invalid			duplicate
// 
//*****************************************************************
// Raised when a file has been successfully uploaded 
eventEmitter.on('file-uploaded', onFileUploaded);
// Raised when file has been validated
eventEmitter.on('file-validated', onFileValidated);
//Raised when file is invalid
eventEmitter.on('file-invalid', onFileInvalid);
//Raised when no duplicate found
eventEmitter.on('file-not-duplicate', onFileNotDuplicate);
//Raised when duplicate found
eventEmitter.on('file-duplicate', onFileDuplicate);
// Raised when a file has been successfully logged
eventEmitter.on('file-logged', onFileLogged);
//Raised when a clery parse task has been queued
eventEmitter.on('task-queued', onTaskQueued);

//*****************************************************************
//					EVENT HANDLERS
//*****************************************************************
function onFileUploaded(file, req, res)
{
	_validateFile(file, req, res);
}
function onFileValidated(file, req, res)
{
	_checkForDuplicate(file, req, res);
}
function onFileInvalid(file, req, res)
{
	_exitDeletingFile(file, req, res);
}
function onFileNotDuplicate(file, req, res)
{
	_logFile(file, req, res);
}
function onFileDuplicate(file, req, res)
{
	_exitDeletingFile(file, req, res);
}
function onFileLogged(file, req, res)
{
	_queueParsingTask(file, req, res);
}
function onTaskQueued(file, req, res)
{
	res.end('Hand history successfully uploaded!');
}

//*****************************************************************
//				UTILITY FUNCTIONS
//*****************************************************************
function _exitDeletingFile(file, req, res)
{
	console.log('exiting, deleting file');
	fs.unlink(file.path);
	res.end('File not uploaded');
}
function _validateFile(file, req, res)
{
	// TODO, validate for security
	eventEmitter.emit('file-validated', file, req, res);
	//if not validated: eventEmitter.emit('file-invalid', file, req, res);
}
function _checkForDuplicate(file, req, res)
{
	// check for duplicate
	fileLogClient.get(file.name,
		function(err, obj)
		{
			if(err)
			{
				console.log('onFileValidated: fileLog error: ' + err.message);
				return _exitDeletingFile(file, req, res);
			}
			if(obj)
			{
				console.log('onFileValidated: duplicate file');
				eventEmitter.emit('file-duplicate', file, req, res);
			}
			else
			{
				eventEmitter.emit('file-not-duplicate', file, req, res);
			}
		});
}
function _logFile(file, req, res)
{
	// File is validated and not a duplicate => log file and proceed
	fileLogClient.add(file.name, 
		function(err)
		{
			if(err)
			{
				console.log('onFileNotDuplicate: fileLog error: ' + err.message);
				return _exitDeletingFile(file, req, res);
			}
			else
			{
				eventEmitter.emit('file-logged', file, req, res);
			}
		});
}
function _queueParsingTask(file, req, res)
{
	taskQueueClient.add(file.name,
			function(err)
			{
				if(err)
				{
					console.log('onFileLogged: taskQueue error: ' + err.message);
					return _exitDeletingFile(file, req, res);
				}
				else
				{
					eventEmitter.emit('task-queued', file, req, res);
				}
			});
}