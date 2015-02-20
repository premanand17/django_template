
(function( results_pagination, $, undefined ) {
	
	results_pagination.build = function(paginationId, overviewId, query, db, size, total) {
		var npages = total / size;
		if(size < total) {
			$('#'+overviewId).html('Showing '+size+' of '+total+' hits');
		} else {
			$('#'+overviewId).html('Showing '+total+' of '+total+' hits');
		}
		$('#'+paginationId).empty();
		$('#'+paginationId).append('<ul class="pagination pagination-sm" id="search-pagination" style="margin: 0;"></ul>');
		$('#search-pagination').append('<li><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>');
		$('#search-pagination').append('<li class="active"><a href="#">1</a></li>');
		for (i = 2; i < npages+1; i++) {
			$('#search-pagination').append('<li><a href="#">'+i+'</a></li>');
		}
		$('#search-pagination').append('<li><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>');
		
		$('#search-pagination').on( "click", "li", function() {
			updateResults(this, db, size, query);
		});
		updateResults($('.active'), db, size, query);
		if(npages === 1) {
			$('#search-pagination').children("li").first().addClass("disabled");
			$('#search-pagination').children("li").last().addClass("disabled");
		}
		addDropDownSize(paginationId, overviewId, query, db, size, total);
	}
	
	addDropDownSize = function(paginationId, overviewId, query, db, size, total) {
		var sizerId = paginationId+'-sizer';
		$('#'+paginationId).append('<div class="btn-group pull-right">'+
				'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">'+
				'  Per Page <span class="caret"></span>'+
				'</button>'+
				'<ul id="'+sizerId+'" class="dropdown-menu" role="menu"></ul>'+
				'</div>');
		$('#'+sizerId).append('<li><a href="#">10</a></li>');
		$('#'+sizerId).append('<li><a href="#">20</a></li>');
		$('#'+sizerId).append('<li><a href="#">50</a></li>');
		$('#'+sizerId).append('<li><a href="#">100</a></li>');
		
		$('#'+sizerId).on( "click", "li", function() {
			results_pagination.build(paginationId, overviewId, query, db, $(this).text(), total);
		});
	}
	
	// update results when a new page number is clicked
	updateResults = function(thisPage, db, size, query) {
		var url = 'http://'+window.location.host +'/'+db+'/_search?';
		var page = $( thisPage ).text().match(/[0-9]+/);
		if( page === null ) {
			var label = $( thisPage ).children('a').first().attr('aria-label');
			if(label === 'Next') {
				$('.active').next().trigger('click');
			} else {
				$('.active').prev().trigger('click');
			}
			return;
		}

        var es_from = (((page[0]-1)*size));
        var es_data = JSON.stringify({
				"from" : es_from, "size" : size,
				"query": query
				});
        $('.active').removeClass('active');
        $('span .pagination-sr').remove();
        $(thisPage).addClass('active');
        $(thisPage).siblings('a').append('<span class="sr-only" id="pagination-sr">(current)</span>');
        $.ajax({
        	url: url,
        	dataType: "json",
        	type: "POST",
        	data: es_data,
        	success: function(json){
        		$('#results').empty();
        		var hits = json.hits.hits;
        		for(var i=0; i<hits.length; i++) {
        			var hit = hits[i]._source;
        			$('#results').append(
					'<ul class="list-group">' +
					'<li class="list-group-item"><a href="/marker/'+hit.ID+'">'+hit.ID+'</a></li>'+
					'<li class="list-group-item">Chromosome: '+hit.SRC+'; Position: '+hit.POS+'; '+
					                        hit.REF+'/'+hit.ALT+'</li>'+
			  		'</ul>');	
        		}
        	}
        });
	}

}( window.results_pagination = window.results_pagination || {}, jQuery ));