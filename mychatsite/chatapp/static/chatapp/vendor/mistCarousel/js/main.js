(function($){

	"use strict";

	$(document).ready(function() {

		// default initialization
		// autoplaySpeed : 5000, dots: true
		//$('#mistify').mistify();

		// custom initialization
		if ($('#mistify').length) {
			$('#mistify').mistify({
				arrows: true,
				autoPlay: true,
				autoplaySpeed: 15000,
				dots: true,
				readMoreText: 'More'
			});
		}

		$('.scroll-top').on('click', function(e) {
			e.preventDefault();
			$('html, body').animate({ scrollTop: 0 }, 'slow');
		});

		$('.mist-link').on('click', function(e) {
			e.preventDefault();
			var url = $(this).attr('href');
			$('body').addClass('overlay-wrapped');
			$('.mist-overlay').addClass('slideInReady').show();
			setTimeout(function() {
				$('.mist-overlay').addClass('slideIn');
			}, 100);

			setTimeout(function() {
				window.location.href = url;
			}, 2200);
		});

		$('.inner-page__prev-post, .inner-page__next-post')
			.on('mouseover', function() {
				$(this).addClass('active');
			})
			.on('mouseout', function() {
				$(this).removeClass('active');
			});
	});

	$(window).on('load', function() {
		$('body').removeClass('overlay-wrapped');
		$('.mist-overlay').addClass('slideOut');
		setTimeout(function() {
			$('.mist-overlay').hide().removeClass('slideOut');
		}, 2200);
	});
})(jQuery);