module.exports = FileValidator;

var xssFilters = require('xss-filters');
var validator = require('validator');

function FileValidator(options)
{
	this.validateFileProperties = FileValidator.validateFileProperties;
	this.extension = options.extension;
	this.mimetype = options.mimetype;
	this.pattern = options.pattern;
	if ( options.log )
	{
		this.log = options.log.child({module: 'fileLog'});
	}
}

FileValidator.validateFileProperties = function(file)
{
	if ( this.extension )
	{
		if ( xssFilters.inHTMLData(file.extension) != this.extension )
		{
			if (this.log) this.log.warn('invalid extension: ' + xssFilters.inHTMLData(file.originalname) );
			return false;
		}
	}
	if ( this.mimetype )
	{
		if ( xssFilters.inHTMLData(file.mimetype) != this.mimetype )
		{
			if (this.log) this.log.warn('invalid mimetype: ' + xssFilters.inHTMLData(file.originalname) );
			return false;
		}
	}
	if ( this.encoding )
	{
		if ( xssFilters.inHTMLData(file.encoding) != this.encoding )
		{
			if (this.log) this.log.warn('invalid encoding: ' + xssFilters.inHTMLData(file.originalname) );
			return false;
		}
	}
	if ( this.pattern )
	{
		if ( !validator.matches(xssFilters.inHTMLData(file.originalname), this.pattern) )
		{
			if (this.log) this.log.warn('invalid file name: ' + xssFilters.inHTMLData(file.originalname) );
			return false;
		}
	}
	return true;
};
