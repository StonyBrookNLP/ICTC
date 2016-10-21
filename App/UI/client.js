$(function () {
    $('#input_form').on('submit', function (e) {
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (data)
            {
                $("#input_form :input").prop("disabled", true);
                $("#response_img").attr("src", data['meme_url']).attr("alt", data['response']);
                $("#response_text").html(data['response']);
                $("#feedback_form").show();
            }
        });
        e.preventDefault();
    })

    $('#feedback_form').on('submit', function (e) {
        var feedback_data = {}
        feedback_data['bot'] = $("#input_form input[name=optionsBot]:checked").val();
        feedback_data['inp_text'] = $("#input_text").val();
        feedback_data['response_text'] = $("#response_text").text();
        var content_score = $("#feedback_form input[name=optionsContent]:checked").val();
        var style_score = $("#feedback_form input[name=optionsStyle]:checked").val();
        feedback_data['content_score'] = parseInt(content_score, 10);
        feedback_data['style_score'] = parseInt(style_score, 10);

        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: JSON.stringify(feedback_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data)
            {
                $("#feedback_form :input").prop("disabled", true);
                $("#thanks_div").show();
            }
        });
        e.preventDefault();
    })
});