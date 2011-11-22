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

    return veresedaki;
}


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
            url: '/api/v1/login/',
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
	user.emailmd5 + '?s=48&d=identicon';
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

// function to initialize #activity page
function initiliaze_activity_page() {
    $.getJSON("/api/v1/transaction/list/", populate_transactions);
}

// function to initialize #connections page
function initiliaze_connections_page() {
    $.getJSON("/api/v1/relation/list/", populate_relations);
}


// function to initialize #dashboard page
function initiliaze_dashboard_page() {
   $.getJSON("/api/v1/profile/", populate_profile);
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
	url:'/api/v1/logout/',
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
		url:'/api/v1/profile/',
		dataType: 'text',
		data:$(this).serialize(),
		success: success_cb,
		error: error_cb
	    });
	    return false;
	}
    )
}


function populate_profile(json) {
    // check if new user
    if (json.data.first_name == '')
	$.mobile.changePage('#welcome', '#welcome');

    window.my_name = json.data.first_name + ' ' + json.data.last_name;
    window.my_email = json.data.email;

}

function populate_relations(json) {
    $('#relation_list').empty();
    var ddata = [];

    $.each(json.data.relations,
           function(key, value) {
	       if (user_is_me(value.user1) == true)
		   user = value.user2;
	       else
		   user = value.user1;

	       img = get_gravatar_url(user);
	       name = get_full_name(user);

	       ddata.push({
			      'balance': value.balance,
			      'name': name,
			      'currency': value.currency,
			      'id': value.id,
			      'img': img,
			      'updated': value.updated
			  });
	   }
	  );

    $("#relationItem").tmpl(ddata).appendTo("#relation_list");

    // pretty dates, updated once per minute
    $(".relation_date").prettyDate({interval:60000});

    $("#relation_list").listview("refresh");

}

function populate_transactions(json) {
    $('#transaction_list').empty();
    var ddata = [];

    $.each(json.data.transactions,
	   function(key, value)
	   {
	       // if payer is me
	       if (user_is_me(value.payer) == true) {
	       	   // if more than one owers
	       	   if (value.veresedakia.length > 1) {
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
		   item_sign = '';
	       }
	       // i'm ower
	       else {
		   item_sign = '-';
	       	   item_img = get_gravatar_url(value.payer);
	       	   item_name = get_full_name(value.payer);
 	       	   item_amount = find_my_veresedaki(value.veresedakia).amount + ' ' + value.currency.symbol;
	       }

	       if (value.status == "Accepted") {
		   // set icon
		   item_icon = 'check';

		   // set details
		   item_details = $('#transactionConfirmed').tmpl({})[0].innerHTML;
	       }

	       else {
		   // set icon
		   item_icon = 'alert';

		   // set details
		   window.e = $('#transactionUnconfirmed').tmpl({});
		   item_details = $('#transactionUnconfirmed').tmpl({})[0].innerHTML;
	       }

	       ddata.push({
		   'id': value.id,
	       	   'img': item_img,
	       	   'name': item_name,
	       	   'comment':value.comment,
	       	   'amount': item_amount,
	           'date': value.created,
	           'location': 'unknown location',
		   'icon': item_icon,
	           'sign': item_sign,
	       	   'currency_code': value.currency.code,
	           'details': item_details
	       });

	       $('#transaction-' + value.id).die();
	       $(document).delegate('#transaction-' + value.id,
				    'click',
				    function(event) {
					if ($('#' + event.target.parentNode.id + '-details').is(":visible") == false)
					    toggle_only = true;
					else
					    toggle_only = false;

					if (toggle_only == true)
					    $(".transaction-item-details").slideUp();

					$('#transaction-' + value.id + '-details').slideToggle();
					});

	   }
	  ); // end each();

    $("#transactionItem").tmpl(ddata).appendTo("#transaction_list");

    // pretty dates, updated once per minute
    $(".transaction_date").prettyDate({interval:60000});

    $(".transaction-item-details").trigger('create');

    $("#transaction_list").listview("refresh");

}


// lives
$('#login').live('pagebeforeshow', initiliaze_login_page);
$('#dashboard').live('pagebeforeshow', initiliaze_dashboard_page);
$('#activity').live('pagebeforeshow', initiliaze_activity_page);
$('#connections').live('pagebeforeshow', initiliaze_connections_page);
$('#welcome').live('pagebeforeshow', initiliaze_welcome_page);
$('#logout').live('pagebeforeshow', initiliaze_logout_page);


// init
$(window).bind("orientationchange resize pageshow", _fixgeometry);
