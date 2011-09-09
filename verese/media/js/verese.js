function populate_currencies(json) {
  // populate balance
    $('#balance_aggregation').html(
        parseFloat(json.data.balance_aggregation.balance).toFixed(2) +
            json.data.balance_aggregation.currency.symbol
    ).trigger('create');

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

    $('#currency_aggregations').trigger('create');
}

function set_profile(json) {
    $('#myname').html(json.data.first_name + ' ' + json.data.last_name);
}

function populate_transactions(json) {
    $.each(json.data.transactions,
	   function(key, value)
	   {
	       var list_item = '' +
	       	   '<li class"list_item">' +
	       	   '<a href="index.html">' +
	       	   '<img src="http://www.gravatar.com/avatar/' +
	       	   value.payer.emailmd5 +
	       	   '?s=80&d=mm" />' +
	       	   '<h3>Broken Bells</h3>' +
	       	   '<p>Broken Bells</p>' +
	       	   '</a>' +
	       	   '</li>';

	       $('#transaction_list').append(list_item);
	   }
	  ); // end each();

    $('#transaction_list').trigger('create');

}
