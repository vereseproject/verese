var my_email = null;

function whoami() {
    return window.my_email;
}

function populate_balance(json) {
    // populate balance
    $('#balance_aggregation').html(
        parseFloat(json.data.balance_aggregation.balance).toFixed(2) +
            json.data.balance_aggregation.currency.symbol
    );
    $('#balance_aggregation').attr('data-role', 'button');
    $('#balance_aggregation').attr('data-icon', 'grid');
    $('#balance_aggregation').attr('data-iconpos', 'bottom');
    $('#balance_aggregation').parent().trigger('create');

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
		   '<h2>' + value.currency.symbol + '<br/>' + value.balance  + '</h2>' +
		   '</a>';

    	       $('#currency_aggregations').append(button_text);//.trigger('create');

	       $('#' + value.currency.code + '_transactions_button').click(function() {
	       	   $('.' + value.currency.code + '_transaction').slideToggle('fast');
	       });

    	   }
    	  ); // end each()

    $('#currency_aggregations').parent().trigger('create');
}

function populate_profile(json) {
    $('#my_name').html(json.data.first_name + ' ' + json.data.last_name);
    $('#my_avatar').html('<img src="http://www.gravatar.com/avatar/' +
			 json.data.emailmd5 +
			 '?s=80&d=mm" />'
			);

    window.my_email = json.data.email;
}

function user_is_me(user) {
    // acceptes a json object poiting to a user,
    // returns True is this is me
    // false otherwise
    if (user.email == my_email)
	return true;
    else
	return false;
}

function get_gravatar_url(user) {
    // acceptes a json object poiting to a user,
    // returns True gravatar image url
    return 'http://www.gravatar.com/avatar/' +
	user.emailmd5 + '?s=80&d=mm'
}

function get_full_name(user) {
    // aceepts a json object poiting to a user
    // return string with full name
    return user.first_name + ' ' + user.last_name;
}

function get_amount_repr(item) {
    return item.amount + ' ' + item.currency.symbol;
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
    $.each(json.data.transactions,
	   function(key, value)
	   {
	       // if payer is me
	       if (user_is_me(value.payer) == true) {
		   // if more than one owers
		   if (value.veresedakia.length > 1) {
		       item_img = '/media/images/app/multiple.png';

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

	       var list_item = '' +
	       	   '<li class="ui-li-has-arrow ' + value.currency.code + '_transaction" data-icon="arrow-d">' +
	       	   '<a href="index.html">' +
	       	   '<img src="' + item_img + '" />' +
	       	   '<h3>' + item_name + '</h3>' +
	       	   '<p>' + value.comment + ' at ' + 'Kifisias Avenue 123' + '</p>' +
	       	   '</a>' +
		   '<p class="ui-li-count">' + item_amount +'</div>' +
	       	   '</li>';

	       $('#transaction_list').append(list_item);
	   }
	  ); // end each();


    $('#transaction_list').attr('data-role', 'listview');
    $('#transaction_list').parent().trigger('create');

}
