$(function () {

    $('#input_bubble').hide();
    $('#response_bubble').hide();

    if ($(window).width() <= 768) {
        $("#bubble_wrapper").before($("#trump_opt_wrapper"));
    }

    $("#input_form input[name=optionsBot]").on('change', function(e) {
        var bot = $("#input_form input[name=optionsBot]:checked").val();

        if (bot == 't') {
            $("#input_bubble")
                .removeClass()
                .addClass("bubble left")
                .css('float', 'left')
                .attr('data-placeholder', "Type in something Clinton would say to see what Trump-a-bot says back")
                .text("")
                .show()
                .focus();
        } else {
            $("#input_bubble")
                .removeClass()
                .addClass("bubble right")
                .css('float', 'right')
                .attr('data-placeholder', "Type in something Trump would say to see what Clinton-a-bot says back")
                .text("")
                .show()
                .focus();
        }
    });

    var submitForm = function (e) {
        if (e.which == 13) {
            $(this).closest('form').submit();
            return false;
        }
    };

    $('.input').keypress(submitForm);
    $('#input_bubble').keypress(submitForm);

    $('#input_form').on('submit', function(e) {
        e.preventDefault();

        var inp_text = $("#input_bubble").text();
        if (!inp_text) {
            alert("Please enter an argument for the other side");
            return;
        }
        $('body').addClass('wait');
        var bot = $("#input_form input[name=optionsBot]:checked").val();
        if (bot == 't') {
            $("#response_bubble")
                .removeClass()
                .addClass( "bubble right" )
                .css('float', 'right')
                .html('Trump-a-bot processing....')
                .show();
        } else {
            $("#response_bubble")
                .removeClass()
                .addClass( "bubble left" )
                .css('float', 'left')
                .html('Clinton-a-bot processing....')
                .show();
        }
        var post_data = {
            message: inp_text,
            optionsBot: bot
        };
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: post_data,
            success: function (response)
            {
                $('body').removeClass('wait');
                $("#response_bubble").html(response);

                $("#translate_btn").hide();
                $("#feedback_form").show();
            }
        });

        $("#input_form :input").prop("disabled", true);
        $('#input_bubble').attr('contenteditable', 'false');

        // customize feedback form for the candidate
        var candidate = bot == 't' ? 'Trump' : 'Clinton';
        $("#candidate_name").html(candidate);

        $("#feedback_form .candidate-name").each(function(i) {
            $(this).text(candidate);
          });
        if (bot == 't') {
            $("#content_question").html("Was Trump's response about the same topic as what you typed for Clinton?");
        } else {
            $("#content_question").html("Was Clinton's response about the same topic as what you typed for Trump?");
        }

    });

    $('#feedback_form').on('submit', function(e) {
        var feedback_data = {}
        feedback_data['bot'] = $("#input_form input[name=optionsBot]:checked").val();
        feedback_data['inp_text'] = $("#input_bubble").text();
        feedback_data['response_text'] = $("#response_bubble").text();
        var content_score = $("#feedback_form input[name=optionsContent]:checked").val();
        var style_score = $("#feedback_form input[name=optionsStyle]:checked").val();
        feedback_data['content_score'] = parseInt(content_score, 10);
        feedback_data['style_score'] = parseInt(style_score, 10);
        var suggestion_text = $("#suggestion_text").val();
        if (!suggestion_text) {
            suggestion_text = ""
        }
        feedback_data['suggestion_text'] = suggestion_text;
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: JSON.stringify(feedback_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data)
            {
                $("#feedback_form :input").prop("disabled", true);
                $("#thanks_modal").modal({backdrop: "static"});
            }
        });
        e.preventDefault();
    });

    var checkLowScore = function() {
        var content_score = $("#feedback_form input[name=optionsContent]:checked").val();
        var style_score = $("#feedback_form input[name=optionsStyle]:checked").val();
        content_score = parseInt(content_score, 10);
        style_score = parseInt(style_score, 10);

        if (content_score < 3 || style_score < 3) {
            $("#suggestion_wrapper").show();
        } else {
            $("#suggestion_wrapper").hide();
        }
    };

    $("#feedback_form input[name=optionsContent]").on('change', checkLowScore);

    $("#feedback_form input[name=optionsStyle]").on('change', checkLowScore);

    $('#thanks_modal').on('hidden.bs.modal', function(e) {
        window.location.reload();
    });

    $('#thanks_modal').on('shown.bs.modal', function () {
        $('#modal_close_button').focus();
    });
});