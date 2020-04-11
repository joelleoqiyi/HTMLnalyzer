    var notification_prototype = document.getElementById("notification_prototype");
    document.addEventListener('DOMContentLoaded', () => {
        'use strict';

        notification_prototype.className = "show";
        setTimeout(function(){
          notification_prototype.className = notification_prototype.className.replace("show", "");
        }, 5800);
    });
