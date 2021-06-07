$(document).ready(function () {
    var phone = '';
    var deltime = 1;
    var paytype = 0;
    let price = parseFloat($('#orderPrice').html());
    var pers = 1;

    $('#pay_courier').click(function () {
        paytype = 0;
    });
    $('#pay_online').click(function () {
        paytype = 1;
    });
    // $('#del_morning').click(function () {
    //     deltime = 0;
    // });
    // $('#del_evening').click(function () {
    //     deltime = 1;
    // });
    $('#get_sms_btn').click(function () {
        $('#check_code_block').show();
        let mPhone = $('#order_phone').val();
        phone = mPhone;
        $.ajax({
            url: "/api/clients/auth",
            data: JSON.stringify({
                phone: mPhone
            }),
            contentType: 'application/json;charset=UTF-8',
            method: 'POST',
            success: function (response) {
            },
            error: function (error) {
            }
        });
    });
    $('#check_code_btn').click(function () {
        let mPhone = phone;
        let code = $('#order_checkcode').val();
        $.ajax({
            url: "/api/clients/checkcode",
            data: JSON.stringify({
                phone: mPhone,
                checkCode: code
            }),
            contentType: 'application/json;charset=UTF-8',
            method: 'POST',
            success: function (response) {
                $('#client_info_block').show();
                $('#order_info_block').show();
            },
            error: function (error) {
                alert('Ошибка');
            }
        });
    });

    $('#order_persons').change(function(){
        pers = parseFloat($(this).val());
        $('#finish_price').html(price*pers);
    });



    $('#promocode_btn').click(function () {
        let promocode = $('#order_promocode').val();
        let cprice = price * pers;
        if (parseFloat(price) == 500 || parseFloat(price) == 750) {
            $('#promo_msg').html('Промокод действителен при заказе от 5 дней');
        }
        else {
            $.ajax({
                url: "/api/promocodes/count",
                data: JSON.stringify({
                    promocode: promocode,
                    price: cprice
                }),
                contentType: 'application/json;charset=UTF-8',
                method: 'POST',
                success: function (response) {
                    let mJson = JSON.parse(JSON.stringify(response));
                    let newPrice = mJson.newprice;
                    if (parseFloat(newPrice) == parseFloat(cprice))
                        $('#promo_msg').html('Промокод недействителен')
                    else {
                        $('#promo_msg').html('Скидка: ' + (parseFloat(newPrice) - parseFloat(cprice)))
                        $('#finish_price').html(newPrice);
                    }
                },
                error: function (error) {

                }
            });
        }

    });
    $('#order_btn').click(function () {
        if (paytype == 0) {
            let name = $('#order_name').val();
            let surname = $('#order_surname').val();
            let email = $('#order_email').val();
            let city = $('#order_city').val();
            let street = $('#order_street').val();
            let house = $('#order_house').val();
            let flat = $('#order_flat').val();
            var promocode = 'empty'
            if ($('#order_promocode').val() != '') {
                promocode = $('#order_promocode').val();
            }
            let mDeltime = deltime;
            let mPaytype = paytype;
            let ordertype = $('#orderType').html();
            let orderdays = $('#orderDays').html();
            let orderfoods = $('#orderFoods').html();
            let deldate = $('#order_prefdate').val()
            let orderpersons = $('#order_persons').val()

            $.ajax({
                url: "/api/clients/addorder_offline",
                data: JSON.stringify({
                    phone: phone,
                    name: name,
                    surname: surname,
                    email: email,
                    city: city,
                    street: street,
                    house: house,
                    flat: flat,
                    promocode: promocode,
                    mDeltime: mDeltime,
                    paytype: mPaytype,
                    ordertype: ordertype,
                    orderdays: orderdays,
                    orderfoods: orderfoods,
                    orderpersons: orderpersons,
                    deldate: deldate
                }),
                contentType: 'application/json;charset=UTF-8',
                method: 'POST',
                success: function (response) {
                    window.open('/')
                },
                error: function (error) {

                }
            });
        }
        else {
            let name = $('#order_name').val();
            let surname = $('#order_surname').val();
            let email = $('#order_email').val();
            let city = $('#order_city').val();
            let street = $('#order_street').val();
            let house = $('#order_house').val();
            let flat = $('#order_flat').val();
            var promocode = 'empty'
            if ($('#order_promocode').val() != '') {
                promocode = $('#order_promocode').val();
            }
            let ordersum = $('#finish_price').html();
            let mDeltime = deltime;
            let mPaytype = paytype;
            let ordertype = $('#orderType').html();
            let orderdays = $('#orderDays').html();
            let orderfoods = $('#orderFoods').html();
            let deldate = $('#order_prefdate').val()
            let orderpersons = $('#order_persons').val()

            $.ajax({
                url: "/api/clients/addorder_online",
                data: JSON.stringify({
                    phone: phone,
                    name: name,
                    surname: surname,
                    email: email,
                    city: city,
                    street: street,
                    house: house,
                    flat: flat,
                    promocode: promocode,
                    mDeltime: mDeltime,
                    paytype: mPaytype,
                    ordertype: ordertype,
                    orderdays: orderdays,
                    orderfoods: orderfoods,
                    orderpersons: orderpersons,
                    deldate: deldate,
                    ordersum: ordersum
                }),
                contentType: 'application/json;charset=UTF-8',
                method: 'POST',
                success: function (response) {
                    let mJson = JSON.parse(JSON.stringify(response));
                    let payment_url = mJson.payment_url;
                    window.open(payment_url)
                },
                error: function (error) {

                }
            });
        }
    })
});