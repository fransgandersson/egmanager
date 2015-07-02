$(document).ready(
	function()
	{
		getRecentUploads();
		var form = document.forms.namedItem("formSubmitFile");
		form.addEventListener('submit', 
			function(event) 
			{
				var data = new FormData(form);
				var req = new XMLHttpRequest();
				req.open("POST", "api/uploads", true);
				req.onload = 
					function(resp) 
					{
						console.log(resp);
				 		if (req.status == 200) 
				 		{
				 			getRecentUploads();
				 		} 
				 		else 
				 		{
				 		}
					};
		
				req.send(data);
				event.preventDefault();
			}, false);
	});
function getRecentUploads()
{
    $.ajax(
    {
        type : 'GET', 
        url : 'api/uploads',
        data : {count: 5},
        dataType : 'json', 
        encode : true
    }).done(function(data)
    	{
    		listUploads(data);
    	});
}
function listUploads(data)
{
	var ul = $('#ulRecentUploads');
	ul.empty();
	$.each(data, 
		function(i)
		{
			var s = new Date(data[i].time).toLocaleString() + ': ' + data[i].file; 
			var li = $('<li></li>').appendTo(ul);
			var a = $('<a/>').text(s).appendTo(li);
		});
}