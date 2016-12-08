$(function () {

    var user_id = Cookies.get('user_id');
    var order_id = Cookies.get('order_id');
    var bot = Cookies.get('bot');
    var input = Cookies.get('input');
    var response1 = Cookies.get('response1');
    var response2 = Cookies.get('response2');

    $("#input_text").text(input);
    $("#response1").text(response1);
    $("#response2").text(response2);

    if (window.location.search) {
        $('#thanks_div').show();
        window.history.pushState(null, "", window.location.origin);
    }

    var submitForm = function(e) {
        if (e.which == 13) {
            $(this).closest('form').submit();
            return false;
        }
    };

    $('.input').keypress(submitForm);

    $('#feedback_form').on('submit', function(e) {
        e.preventDefault();
        alert('called');
        $('body').addClass('wait');
        var feedback_data = {}
        feedback_data['order_id'] = order_id;
        feedback_data['content_score1'] = $("#feedback_form input[name=optionsContent1]:checked").val();
        feedback_data['content_score2'] = $("#feedback_form input[name=optionsContent2]:checked").val();
        feedback_data['style_score1'] = $("#feedback_form input[name=optionsStyle1]:checked").val();
        feedback_data['style_score2'] = $("#feedback_form input[name=optionsStyle1]:checked").val();
        feedback_data['comparision'] = $("#feedback_form input[name=optionsCompare]:checked").val();
        for (var name in feedback_data) {
            feedback_data[name] = parseInt(feedback_data[name], 10);
        }
        feedback_data['user_id'] = user_id;
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: JSON.stringify(feedback_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response)
            {
                $('body').removeClass('wait');
                window.location.reload();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert("Error code:" + xhr.status + ". Sorry, there was an error submitting feedback. Refreshing the page.");
                window.location.reload();
            }
        });

        $("#input_form :input").prop("disabled", true);
        return false;
    });


});
