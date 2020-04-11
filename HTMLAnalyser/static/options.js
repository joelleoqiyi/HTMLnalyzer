    var form_options = document.getElementById("html_form_options");
    var notification_instructions = document.getElementById("notification_instructions");
    var notification_instructions_top = document.getElementById("notification_instructions_top");
    document.addEventListener('DOMContentLoaded', () => {
        'use strict';

        notification_instructions_top.className = "show";
        setTimeout(function(){
          notification_instructions_top.className = notification_instructions_top.className.replace("show", "");
          notification_instructions_top.innerHTML = "Click ENTER to start analysis..";
          notification_instructions_top.className = "show";

        }, 5800);


        document.addEventListener('keydown', event => {
          if (event.key == "Enter"){
            form_options.submit();
            //alert("this is amazing!!");
          };
        });
    });
