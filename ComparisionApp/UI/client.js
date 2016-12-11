$(function () {
    var user_id = Cookies.get('user_id');
    var order_id = Cookies.get('order_id');
    var bot = Cookies.get('bot');

    if (order_id == -1) {
        // We are done with all questions
        alert('Thank you! We have reached our survey target!');
        // Closing tab
        window.close();
    } else if (order_id == -2) {
        // We are done for this user
        alert('Thank you! You are done with all the questions!');
        // Remove the user_id so someone else can answer these
        // Or the same user can restart
        Cookies.remove('user_id');
        window.location.reload();
    }

    if (bot == 'c') {
        var candidate = 'Trump';
        var opponent = 'Clinton';
    } else {
        var candidate = 'Clinton';
        var opponent = 'Trump';
    }

    $(window).on('unload', function() {
        $(window).scrollTop(0);
    });

    $("#candidate_img").attr('src', candidate + "/podium.jpg");

    $("#feedback_form img[name=opponent-img]").each(function(i) {
        $(this).attr('src', opponent + "/podium.jpg");
    });

    $("#feedback_form .candidate-name").each(function(i) {
        $(this).text(candidate);
    });

    $("#feedback_form .opponent-name").each(function(i) {
        $(this).text(opponent);
    });

    var submitFeedback = function(e) {
        if (e.which == 13) {
            $('#feedback_form').submit();
            return false;
        }
    };

    $('.input').keypress(submitFeedback);

    $('#feedback_form').on('submit', function(e) {
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
