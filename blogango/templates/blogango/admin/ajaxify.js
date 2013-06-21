<script>
    $(document).ready(function(){
        $(".block_comment").click(function(){
            var pk = $(this).attr("value");
            $.ajax({
                type: "POST",
                url: '{% url "blogango_admin_comment_block" %}',
                data: {'csrfmiddlewaretoken': '{{csrf_token}}', 'comment_id':pk},
                success: function(data, textStatus){
                    $('a[value='+ data + ']').parents("li").remove();
                },
            });
        });
        $(".approve_comment").click(function(){
            var pk = $(this).attr("value");
            $.ajax({
                type: "POST",
                url: '{% url "blogango_admin_comment_approve" %}',
                data: {'csrfmiddlewaretoken': '{{csrf_token}}', 'comment_id':pk},
                success: function(data, textStatus){
                    $('a[value='+ data + ']').parents("li").remove();
                },
            });
        });
    });
</script>
