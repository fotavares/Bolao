/******************************************
    File Name: custom.js
/****************************************** */

(function ($) {
    "use strict";

    /* ==============================================
    BACK TOP
    =============================================== */
    jQuery(window).scroll(function () {
        if (jQuery(this).scrollTop() > 1) {
            jQuery('.dmtop').css({
                bottom: "75px"
            });
        } else {
            jQuery('.dmtop').css({
                bottom: "-100px"
            });
        }
    });

    /* ==============================================
       LOADER -->
        =============================================== */

    $(window).load(function () {
        $("#preloader").on(500).fadeOut();
        $(".preloader").on(600).fadeOut("slow");
    });



    /* ==============================================
     TOOLTIP -->
     =============================================== */
    $('[data-toggle="tooltip"]').tooltip()
    $('[data-toggle="popover"]').popover()



})(jQuery);

$(document).ready(function () {
    $("input[name='aposta']").change(function () {
        $(this).parentsUntil("tbody").next().removeClass('hidden');
    });
    $("label.butones").click(function () {
        $(this).parentsUntil("tbody").next().removeClass('hidden');
    });
});