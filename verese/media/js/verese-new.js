// variables
var my_email = null;

// function to correct geometry bug
function _fixgeometry() {
    /* Some orientation changes leave the scroll position at something
     * that isn't 0,0. This is annoying for user experience. */
    scroll(0, 0);

    /* Calculate the geometry that our content area should take */
    var header = $("div[data-role='header']:visible");
    var footer = $("div[data-role='footer']:visible");
    var content = $("div[data-role='content']:visible:visible");
    var viewport_height = $(window).height();

    var content_height = viewport_height - header.outerHeight() - footer.outerHeight();
    if((content.outerHeight() + header.outerHeight() + footer.outerHeight())<=viewport_height)
    {
	content_height -= (content.outerHeight() - content.height() + 1);
	content.height(content_height);
    }
    /* Trim margin/border/padding height */
}; /* fixgeometry */


// function to initialize #login page
function initiliaze_login_page() {
    $('#loginform').submit(function(event) {
	event.preventDefault();
	$.mobile.showPageLoadingMsg();

	var success_cb = function(dataReceived, textStatus) {
	    $.mobile.changePage("#dashboard");
	};

	var error_cb = function(dataReceived, textStatus, errorThrown) {
	    alert('login error, try again');
	};

	$.ajax({
            type: 'POST',
            url: '/api/v1.0/login/',
            dataType: 'text',
            data: $(this).serialize(),
            success: success_cb,
            error: error_cb
        });

	// prevent browser from doing anything else
	return false;
    });

    // browserid
    $('#browserid').bind('click', function(e) {
	e.preventDefault();
	navigator.id.getVerifiedEmail(function(assertion) {
            if (assertion) {
		var $e = $('#id_assertion');
		$e.val(assertion.toString());
		$e.parent().submit();
            }
	});
    });
}


// return user's email
function whoami() {
    return window.my_email;
}

// acceptes a json object poiting to a user,
// returns True is this is me
// false otherwise
function user_is_me(user) {
    if (user.email == my_email)
	return true;
    else
	return false;
}

// acceptes a json object poiting to a user,
// returns True gravatar image url
function get_gravatar_url(user) {
    return 'http://www.gravatar.com/avatar/' +
	user.emailmd5 + '?s=80&d=identicon'
}

// accepts a json object poiting to a user
// return string with full name
function get_full_name(user) {
    return user.first_name + ' ' + user.last_name;
}

// represent amount with currency appended
function get_amount_repr(item) {
    return item.amount + ' ' + item.currency.symbol;
}

// function to initialize #dashboard page
function initiliaze_dashboard_page() {
    $('#currency_aggregations').hide();
    $('#balance_aggregation').click(function () {
	$('#currency_aggregations').slideToggle('fast');
    });

    $.getJSON("/api/v1.0/profile/", populate_profile);
    $.getJSON("/api/v1.0/balance/", populate_balance);
    $.getJSON("/api/v1.0/transaction/list/", populate_transactions);
}

// function to initialize #logout page
function initiliaze_logout_page() {
    var success_cb = function(dataReceived, textStatus) {
	$.mobile.changePage("#login");
    };

    var error_cb = function(dataReceived, textStatus, errorThrown) {
	alert('logout error, please try again');
    };

    $.ajax({
	type:'GET',
	url:'/api/v1.0/logout/',
	dataType: 'text',
	data:$(this).serialize(),
	success: success_cb,
	error: error_cb
    });
}

// function to initialize #welcome page
function initiliaze_welcome_page() {
    $('#welcomeform').submit(
	function(event) {
	    event.preventDefault();

	    var success_cb = function(dataReceived, textStatus) {
		$.mobile.changePage("#dashboard", {transition:'pop'});
	    };

	    var error_cb = function(dataReceived, textStatus, errorThrown) {
		alert('update error, please try again');
		// make this a jqm popup or something
	    };

	    // validate
	    if ($('#first_name').val() == '') {
		$('#first_name').focus();
		return false;
	    }
	    else if ($('#last_name').val() == '') {
		$('#last_name').focus();
		return false;
	    }
	    else if ($('#currency').val() == '') {
		$('#currency').focus();
		return false;
	    }

	    $.mobile.showPageLoadingMsg();

	    $.ajax({
		type:'PUT',
		url:'/api/v1.0/profile/',
		dataType: 'text',
		data:$(this).serialize(),
		success: success_cb,
		error: error_cb
	    });
	    return false;
	}
    )
}


function populate_balance(json) {
    // populate balance
    $('#balance_aggregation').html(
        parseFloat(json.data.balance_aggregation.balance).toFixed(2) +
            json.data.balance_aggregation.currency.symbol
    );

    $('#currency_aggregations').empty();
    $.each(json.data.balance_details,
    	   function(key, value)
    	   {
    	       var button_text = '' +
    		   '<a id="' +
    		   value.currency.code +
    		   '_transactions_button" data-role="button" name="' +
    		   value.currency.code +
    		   '_transactions">' +
    		   // '<img src="' + value.currency.image + '">' +
    		   value.currency.symbol + '<br/>' + value.balance +
    		   '</a>';

    	       $('#currency_aggregations').append(button_text);

    	       $('#' + value.currency.code + '_transactions_button').click(function() {
    	       	   $('.' + value.currency.code + '_transaction').slideToggle('fast');
    	       });

    	   }
    	  ); // end each()

    $('#dashboard').trigger('create');
}

function populate_profile(json) {
    $('#my_name').html(json.data.first_name + ' ' + json.data.last_name);
    $('#my_avatar').html('<img width="10%" src="http://www.gravatar.com/avatar/' +
			 json.data.emailmd5 +
			 '?s=80&d=mm" />'
			);

    // check if new user
    if (json.data.first_name == '')
	$.mobile.changePage('#welcome', '#welcome');

    window.my_email = json.data.email;

    $('#dashboard').trigger('create');
}

function find_my_veresedaki(list) {
    // given a list of veresedakia, locate and return mine
    veresedaki = null;

    $.each(list,
	   function(key, value) {
	       if (value.ower.email == window.my_email) {
		   veresedaki = value;
	       }
	   }
	  );

    return veresedaki
}

function populate_transactions(json) {
    $('#transaction_list').empty();
    $.each(json.data.transactions,
	   function(key, value)
	   {
	       // if payer is me
	       if (user_is_me(value.payer) == true) {
		   // if more than one owers
		   if (value.veresedakia.length > 1) {
		       // item_img = '/media/images/app/multiple.png';
		       item_img = 'http://www.gravatar.com/avatar/foo?s=80&d=identicon';

		       item_name = '';
		       $.each(value.veresedakia,
			      function(vkey, vvalue) {
				  item_name += get_full_name(vvalue.ower) + ', ';
			      }
			     );
		       item_name = item_name.substring(0, item_name.length-2);
		   }
		   else {
		       item_img = get_gravatar_url(value.veresedakia[0].ower);
		       item_name = get_full_name(value.veresedakia[0].ower);
		   }

		   item_amount = get_amount_repr(value);
	       }
	       // i'm ower
	       else {
		   item_img = get_gravatar_url(value.payer);
		   item_name = get_full_name(value.payer);
		   item_amount = find_my_veresedaki(value.veresedakia).amount + ' ' + value.currency.symbol;
	       }

	       // arrow direction is different depending on number of owers
	       if (value.veresedakia.length > 1)
		   arrow = "arrow-d";
	       else
		   arrow = "arrow-r";

	       var list_item = '' +
	       	   '<li class="ui-li-has-arrow ' + value.currency.code + '_transaction" data-icon="' + arrow + '">' +
	       	   '<a href="index.html">' +
	       	   '<img src="' + item_img + '" />' +
	       	   '<h3>' + item_name + '</h3>' +
	       	   '<p>' + value.comment + ' at ' + 'Kifisias Avenue 123' + '</p>' +
//	       	   '<p class="transaction_date" title="' + value.created + '">foo' + '</p>' +
	       	   '</a>' +
		   '<p class="ui-li-count">' + item_amount +'</div>' +
	       	   '</li>';

	       $('#transaction_list').append(list_item);
	   }
	  ); // end each();

    // // pretty dates, updated once per minute
    // $(".transaction_date").prettyDate({interval:1000});

    $("#transaction_list").listview("refresh");

}


// lives
$('#login').live('pagebeforeshow', initiliaze_login_page);
$('#dashboard').live('pagebeforeshow', initiliaze_dashboard_page);
$('#welcome').live('pagebeforeshow', initiliaze_welcome_page);
$('#logout').live('pagebeforeshow', initiliaze_logout_page);


// init
$(window).bind("orientationchange resize pageshow", _fixgeometry);
