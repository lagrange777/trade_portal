$(document).ready(function(){
	$('#3xswitch').click(function () {
	    $('.x3menu').css('display', 'inline-flex');
        $('.x5menu').css('display', 'none');
    });
	$('#5xswitch').click(function () {
	    $('.x3menu').css('display', 'none');
        $('.x5menu').css('display', 'inline-flex');
    });

	$('#fast-order').click(function () {
        let name = $('#ff_name').val();
        let phone = $('#ff_phone').val();
        $.ajax({
            url: "/api/clients/addfastorder",
            data: JSON.stringify({
                phone: phone,
                name: name
            }),
            contentType: 'application/json;charset=UTF-8',
            method: 'POST',
            success: function (response) {
                location.reload();
            },
            error: function (error) {
            }
        });
    })
});

