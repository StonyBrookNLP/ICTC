$(function () {
    $('#respond-form').on('submit', function (e) {
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (data)
            {
                alert(data['response']);
                alert(data['meme_src']);
                var responseImg = '<img src="https://i.imgflip.com/1cblat.jpg" class="img-responsive" alt="Trump response">'
                $('#response-wrapper').html(responseImg);
                $('#respond-form')[0].reset();
            }
        });
        e.preventDefault();
    })
});