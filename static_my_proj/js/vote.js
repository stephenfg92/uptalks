
jQuery(document).ready(function($)
    {

    function updateText(selector, newCount){
    	selector.text(newCount)
	}

	function updateColor(selector) {
		var green = "rgb(255, 70, 25)"
    	var gray = "rgb(173, 173, 173)"
    	var color = selector.css('color')

    	if (color == gray){
    		selector.css('color', green)
    	}
    	else {
    		selector.css('color', gray)
    	}

	}


	$(".vote-btn").click(function(e) 
		{
		    e.preventDefault(); 
        	var this_ = $(this)
        	var voteUrl = this_.attr("data-href")

        	var dynCounter = $(this).parents(".row").find(".num")

        	var arrow = $(".far", this)
        	console.log(arrow)


		    $.ajax({
            url: voteUrl,
            method: "GET",
            data: {},
            success: function(data){
              console.log(data)
              if (data.voted) {
              	updateText(dynCounter, data.count)
              	updateColor(arrow)
              }
              else {
              	updateText(dynCounter, data.count)
              	updateColor(arrow)
              }
            }, error: function(error){
              console.log(error)
              console.log("error")
            }
          })
		});
    });