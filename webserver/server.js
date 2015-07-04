'use strict';
// *****************************************************************
//					MODULES
// *****************************************************************
var express = require("express");
var events = require('events');
var multer = require('multer');
var fs = require('fs');
var path = require('path');
var bunyan = require('bunyan');
var validator = require('validator');
var helmet = require('helmet');
var fileLog = require('./filelog/filelog.js');
var fileValidator = require('./filevalidator/filevalidator.js');
var taskQueue = require('./taskqueue/taskqueue.js');

//*****************************************************************
//					APP
//*****************************************************************
var app=express();
app.use(helmet.frameguard('deny'));
app.use(helmet.hidePoweredBy());
app.use(helmet.noSniff());
//*****************************************************************
//				VARIABLES
//*****************************************************************
var PORT = 80;
var LOGLEVEL = 'info';

var sendFileOptions = {root: path.join(__dirname, '/public/')};

var eventEmitter = new events.EventEmitter();
var hhMulter = multer
	({ 
		dest: './uploads/',
		limits:
		{
			fieldNameSize: 80,
			files: 1,
			fileSize: 2000000,
		},
		onFileUploadStart: function (file, req, res) 
		{	
			var valid = fileValidatorClient.validateFileProperties(file);
			if ( !valid )
			{
				res.sendStatus(400);
				return false;
			}
			return true;
		},
		onFileUploadComplete: function (file, req, res)
		{
			if ( !file.truncated )
			{
				eventEmitter.emit('file-uploaded', file, req, res);
			}
			else
			{
				_exitDeletingFile(file, req, res, 'invalid');
			}
		},
	});

//*****************************************************************
//				PAGES
//*****************************************************************
app.use(express.static('public'));
app.get('/',
		function(req,res)
		{
			res.sendFile('index.html', sendFileOptions);
		});
app.get('/upload',
		function(req,res)
		{
			res.sendFile('upload.html', sendFileOptions);
		});

//*****************************************************************
//				API
//*****************************************************************

app.get('/api/uploads',
	function(req,res)
	{
		var n = req.query.count;
		if ( validator.isInt(n, {min: 1, max: 10}) )
		{
			_getUploadedFileByTime(req, res, req.query.count);
		}
		else
		{
			res.sendStatus(400);
		}
	});

app.get('/api/results',
	function(req,res)
	{
		res.sendFile('todo.html', sendFileOptions);
	});

app.post('/api/uploads', hhMulter, 
	function(req,res)
	{
		// handled by multer
	});

app.all('*', 
	function(req, res) 
	{ 
		res.redirect('index.html'); 
	});

app.listen(PORT,
	function()
	{
	    log.info('listening on port ' + PORT);
	});

//*****************************************************************
//				START MODULES
//*****************************************************************
var log = bunyan.createLogger({
	name: 'server', 
	streams: [{
		type: 'rotating-file',
		path: 'server.log',
		period: '1h',
		count: 3}]
});
log.level(LOGLEVEL);
var fileLogClient = new fileLog('uploaded-files', {log: log});
fileLogClient.start();
var fileValidatorClient = new fileValidator({
								log: log, 
								mimetype: 'text/plain', 
								encoding:'7bit', 
								extension:'txt',
								pattern: /HH(\d+) ([A-Za-z]+)( [A-Z]+)? - \$([\w.]+)-\$([\w.]+) - USD 8-Game.txt/});
var taskQueueClient = new taskQueue();
taskQueueClient.start();
//*****************************************************************
//					EVENTS
//  Paths: 
// 		uploaded ->	validated ->	not-duplicate ->	logged ->	task-queued	-> 200
//						|				|
//						v				v
//					invalid			duplicate 	=> 200 + message
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
	_exitDeletingFile(file, req, res, 'invalid');
}
function onFileNotDuplicate(file, req, res)
{
	_logFile(file, req, res);
}
function onFileDuplicate(file, req, res)
{
	_exitDeletingFile(file, req, res, 'duplicate');
}
function onFileLogged(file, req, res)
{
	_queueParsingTask(file, req, res);
}
function onTaskQueued(file, req, res)
{
	res.sendStatus(200);
}

//*****************************************************************
//				UTILITY FUNCTIONS
//*****************************************************************
function _exitDeletingFile(file, req, res, msg)
{
	log.warn('exiting, deleting file: ' + file.name);
	fs.unlink(file.path);
	res.sendStatus(400);
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
	fileLogClient.get(file.originalname,
		function(err, obj)
		{
			if(err)
			{
				log.error('onFileValidated: fileLog error: ' + err.message);
				return _exitDeletingFile(file, req, res, 'server-error');
			}
			if(obj)
			{
				log.warn('onFileValidated: duplicate file: ' + file.name);
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
	fileLogClient.add(file.originalname, file.name, 
		function(err)
		{
			if(err)
			{
				log.error('onFileNotDuplicate: fileLog error: ' + err.message + ' file: ' + file.name);
				return _exitDeletingFile(file, req, res, 'server-error');
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
					log.error('onFileLogged: taskQueue error: ' + err.message + ' file: ' + file.name);
					return _exitDeletingFile(file, req, res, 'server-error');
				}
				else
				{
					eventEmitter.emit('task-queued', file, req, res);
				}
			});
}

function _getUploadedFileByTime(req, res, count)
{
	fileLogClient.getRecent(count, 
			function(err, document)
			{
				if(err)
				{
					log.error('api/uploads: fileLog error: ' + err.message);
					res.sendStatus(500);
				}
				else
				{
					res.end(JSON.stringify(document));
				}
			});
}