$(function () {

    $('#input_bubble').hide();
    $('#response_bubble').hide();
    $('#random_tweet_btn').hide();

    if (window.location.search)
        $('#thanks_div').show();

    var mobile = false;
    if ($(window).width() <= 768) {
        mobile = true;
        $("#bubble_wrapper").before($("#trump_opt_wrapper"));
    }

    clinton_tweets = [
    "latest reckless idea from trump: gut rules on wall street, and leave middle-class families out to dry",
    "climate change is real, and threatens us all."
    ];

    trump_tweets = [
    "why don't we ask the navy seals who killed bin laden? they don't seem to be happy with obama claiming credit. all he did is say .",
    "what do african-americans and hispanics have to lose by going with me. look at the poverty, crime and educational statistics. i will fix it!"
    ];

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
            $('#random_tweet_btn')
                .html("OR Try a random Clinton tweet")
                .show();
        } else {
            $("#input_bubble")
                .removeClass()
                .addClass("bubble right")
                .css('float', 'right')
                .attr('data-placeholder', "Type in something Trump would say to see what Clinton-a-bot says back")
                .text("")
                .show()
                .focus();
            $('#random_tweet_btn')
                .html("OR Try a random Trump tweet")
                .show();
        }

    });

    var submitForm = function (e) {
        if (e.which == 13) {
            $(this).closest('form').submit();
            return false;
        }
    };

    $("#random_tweet_btn").click( function(){
        var bot = $("#input_form input[name=optionsBot]:checked").val();
        var idx = Math.floor(Math.random() * (2));
        if (bot == 't') {
            $("#input_bubble").text(clinton_tweets[idx]);
        } else {
            $("#input_bubble").text(trump_tweets[idx]);
        }
        
        $(this).closest('form').submit();
        return false;
    }); 

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
        $('#random_tweet_btn').hide();
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
        var candidate = bot == 't' ? 'Trump' : 'Clinton';
        var opponent = bot == 't' ? 'Clinton' : 'Trump';
        $("#input_bubble").text(opponent + ": " + inp_text);
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
                $("#response_bubble").html(candidate + "-a-bot: " + response);

                $("#translate_btn").hide();
                $("#feedback_form").show();
            }
        });

        $("#input_form :input").prop("disabled", true);
        $('#input_bubble').attr('contenteditable', 'false');

        // customize feedback form for the candidate
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
        $("#feedback_form :input").prop("disabled", true);
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
                var url = window.location.href;    
                if (url.indexOf('?') == -1)  {
                    url += '?thanks=1';
                }
                window.location.href = url;
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
});