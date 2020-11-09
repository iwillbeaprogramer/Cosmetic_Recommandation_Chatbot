/*
 * Mistify
 * Carousel with fog effect on slide change
 * s.thobi.sinaga@gmail.com
 */

(function() {

	var Mistify = (function() {

		Mistify = function(element, options) {

			var _ = this;

			_.props = {
				activeSlide: 1,
				autoPlayTimer: null,
				elem: $(element),
				lastMask: 1,
				slideCount: 0
			};

			_.options = $.extend({
				arrows: true,
				autoPlay: true,
				autoPlaySpeed: 15000,
				dots: true,
				readMoreText: 'Read more'
			}, options || {});

			_.autoPlay = $.proxy(_.autoPlay, _);
			_.nextSlide = $.proxy(_.nextSlide, _);
			_.stop = $.proxy(_.stop, _);

			_.preloadMasks();

			_.init();
		}

		return Mistify;
	}());

	Mistify.prototype.appendArrows = function() {

		var _ = this;

		var arrowsDom = '' +
			'<div class="mistify__arrows">' +
				'<a href="#" class="mistify__arrows--prev"><i class="fa fa-chevron-up" aria-hidden="true"></i></a>' +
				'<a href="#" class="mistify__arrows--next"><i class="fa fa-chevron-down" aria-hidden="true"></i></a>' +
			'</div>';
		_.props.elem.append(arrowsDom);

		_.props.elem.find('.mistify__arrows--prev').on('click', function(e) {
			e.stopPropagation();
			_.prevSlide();
			_.stop();
			if (_.options.autoPlay) {
				_.autoPlay();
			}
		});

		_.props.elem.find('.mistify__arrows--next').on('click', function(e) {
			e.stopPropagation();
			_.nextSlide();
			_.stop();
			if (_.options.autoPlay) {
				_.autoPlay();
			}
		});
	}

	Mistify.prototype.appendMasks = function() {

		var _ = this;

		var maskDom = '' +
			'<div class="mistify__mask-container">' +
				'<div class="mistify__mask mistify__mask--active"><img src="/static/chatapp/images/mistCarousel-1.png" alt="Mask"/></div>' +
				'<div class="mistify__mask"><img src="/static/chatapp/images/mistCarousel-2.png" alt="Mask"/></div>' +
				'<div class="mistify__mask"><img src="/static/chatapp/images/mistCarousel-3.png" alt="Mask"/></div>' +
				'<div class="mistify__mask"><img src="/static/chatapp/images/mistCarousel-4.png" alt="Mask"/></div>' +
			'</div>';
		_.props.elem.append(maskDom);
	}

	Mistify.prototype.appendDots = function() {

		var _ = this;

		var pagerDom = '<ul class="mistify__dots-container"></ul>';
		_.props.elem.append(pagerDom);

		for (var i = 0; i < _.props.slideCount; i++) {
			var dotsDom = '' +
				'<li class="mistify__dots">' +
					'<span>' + _.props.elem.find('.mistify__slide:nth-child(' + (i + 1) + ') .mistify__slide-timestamp').html() + '</span>' +
				'</li>';
			_.props.elem.find('.mistify__dots-container').append(dotsDom);
		}
		_.props.elem.find('.mistify__dots:nth-child(1)').addClass('mistify__dots--active');

		_.props.elem.find('.mistify__dots').on('click', function(e) {
			e.stopPropagation();
			var elemIndex = _.props.elem.find('.mistify__dots').index(this) + 1;
			_.props.activeSlide = elemIndex;
			_.goToSlide(_.props.activeSlide);
			_.stop();
			if (_.options.autoPlay) {
				_.autoPlay();
			}
		});

		_.props.elem.find('.mistify__dots-container')
			.on('mouseover', function() {
				$(this).addClass('mistify__dots-container--hover');
			})
			.on('mouseout', function() {
				$(this).removeClass('mistify__dots-container--hover');
			});

		_.props.elem.find('.mistify__dots')
			.on('mouseover', function() {
				$(this).addClass('mistify__dots--hover');
			})
			.on('mouseout', function() {
				$(this).removeClass('mistify__dots--hover');
			});
	}

	Mistify.prototype.appendProjectInfo = function() {

		var _ = this;

		var infoContainerDom = '<ul class="mistify__info-container"></ul>';
		_.props.elem.append(infoContainerDom);

		for (var i = 0; i < _.props.slideCount; i++) {
			var infoDom = '' +
				'<li class="mistify__info">' +
					'<a class="mist-link" href="' + _.props.elem.find('.mistify__slide:nth-child(' + (i + 1) + ') .mistify__slide-content').attr('href') + '">' +
						'<p class="mistify__info-description">' +
						'<span class="pull-right">        <i class="fa fa-user" ></i>    </span>&nbsp;' +
						_.props.elem.find('.mistify__slide:nth-child(' + (i + 1) + ') .mistify__slide-description').html() + '</p>' +
						'<p class="mistify__info-title">' +
						'<span class="pull-left">        <i class="fa fa-android" ></i>    </span>&nbsp;' +
						_.props.elem.find('.mistify__slide:nth-child(' + (i + 1) + ') .mistify__slide-title').html() +
						'</p>' +
						'<span class="mistify__info-more">' + _.options.readMoreText + '</span>' +
					'</a>' +
				'</li>';
			_.props.elem.find('.mistify__info-container').append(infoDom);
		}
		_.props.elem.find('.mistify__info:nth-child(1)').addClass('mistify__info--active');
	}

	Mistify.prototype.attachClickHandler = function() {

		var _ = this;

		/* uncomment to make whole elem clickable */
		// _.props.elem.on('click', function() {
		// 	_.nextSlide();
		// 	_.stop();
		// 	if (_.options.autoPlay) {
		// 		_.autoPlay();
		// 	}
		// });

		_.props.elem.find('a').on('click', function(e) {
			e.stopPropagation();
		});
	}

	Mistify.prototype.attachKeyHandler = function() {

		var _ = this;

		$(document).keydown(function(e) {

			switch(e.which) {

				case 37: // left
				break;

				case 38: // up
					_.prevSlide();
					_.stop();
					if (_.options.autoPlay) {
						_.autoPlay();
					}
				break;

				case 39: // right
				break;

				case 40: // down
					_.nextSlide();
					_.stop();
					if (_.options.autoPlay) {
						_.autoPlay();
					}
				break;

				default: return;
			}

			e.preventDefault();
		});
	}

	Mistify.prototype.autoPlay = function() {

		var _ = this;

		if (_.props.autoPlayTimer) {
			clearInterval(_.props.autoPlayTimer);
		}

		_.props.autoPlayTimer = setInterval(_.nextSlide, _.options.autoPlaySpeed);
	}

	Mistify.prototype.goToSlide = function(slideNumber) {

		var _ = this;

		// randomize mist assets image used from 4 selection
		var newMask = Math.floor((Math.random() * 4) + 1);
		while (newMask == _.props.lastMask) {
			newMask = Math.floor((Math.random() * 4) + 1);
		}
		_.props.lastMask = newMask;

		// update mask
		_.props.elem.find('.mistify__mask--active').removeClass('mistify__mask--active');
		_.props.elem.find('.mistify__mask-container .mistify__mask:nth-child(' + newMask + ')').addClass('mistify__mask--active');
		// update slide
		_.props.elem.find('.mistify__slide--active').removeClass('mistify__slide--active');
		_.props.elem.find('.mistify__slide:nth-child(' + slideNumber + ')').addClass('mistify__slide--active');
		// update project info
		_.props.elem.find('.mistify__info--active').removeClass('mistify__info--active');
		_.props.elem.find('.mistify__info:nth-child(' + slideNumber + ')').addClass('mistify__info--active');
		// update pager
		_.props.elem.find('.mistify__dots--active').removeClass('mistify__dots--active');
		_.props.elem.find('.mistify__dots:nth-child(' + slideNumber + ')').addClass('mistify__dots--active');
	}

	Mistify.prototype.init = function() {

		var _ = this;

		_.props.elem.addClass('mistify');
		_.props.activeSlide = 1;
		_.props.elem.find('.mistify__slide').each(function(i) {
			var imgSource = $(this).find('.mistify__slide-background').attr('src');
			$(this).css({
				'background-image': 'url("' + imgSource + '")'
			});
			_.props.slideCount = i + 1;
		});
		_.props.elem.find('.mistify__slide:nth-child(' + _.props.activeSlide + ')').addClass('mistify__slide--active');

		_.appendMasks();
		_.appendProjectInfo();

		if (_.options.dots) {
			_.appendDots();
		}

		if (_.options.arrows) {
			_.appendArrows();
		}

		_.attachClickHandler();
		_.attachKeyHandler();

		if (_.options.autoPlay) {
			_.autoPlay();
		}
	}

	Mistify.prototype.nextSlide = function() {

		var _ = this;

		if (_.props.activeSlide == _.props.slideCount) {
			_.props.activeSlide = 1;
		} else {
			_.props.activeSlide++;
		}

		_.props.elem.find('.mistify__arrows--next').addClass('mistify__arrows--active');
		setTimeout(function() {
			_.props.elem.find('.mistify__arrows--active').removeClass('mistify__arrows--active');
		}, 250);

		_.goToSlide(_.props.activeSlide);
	}

	Mistify.prototype.preloadMasks = function() {

		var _ = this;

		var masks = ['/static/chatapp/images/mistCarousel-1.png', '/static/chatapp/images/mistCarousel-2.png', '/static/chatapp/images/mistCarousel-3.png', '/static/chatapp/images/mistCarousel-4.png']

		for (var i = 0; i < masks.length; i++) {
			$("<img />").attr("src", masks[i]);
		}
	}

	Mistify.prototype.prevSlide = function() {

		var _ = this;

		if (_.props.activeSlide == 1) {
			_.props.activeSlide = _.props.slideCount;
		} else {
			_.props.activeSlide--;
		}

		_.props.elem.find('.mistify__arrows--prev').addClass('mistify__arrows--active');
		setTimeout(function() {
			_.props.elem.find('.mistify__arrows--active').removeClass('mistify__arrows--active');
		}, 250);

		_.goToSlide(_.props.activeSlide);
	}

	Mistify.prototype.resize = function() {

		var _ = this;
	}

	Mistify.prototype.stop = function() {

		var _ = this;

		clearInterval(_.props.autoPlayTimer);
	}

	$.fn.mistify = function (options) {

		var _ = this,
			opt = arguments[0],
			args = Array.prototype.slice.call(arguments, 1),
			ret;

		if (typeof opt == 'object' || typeof opt == 'undefined') {
			_[0].Mistify = new Mistify(_, opt);
		} else {
			ret = _[0].Mistify[opt].apply(_[0].Mistify, args);
		}

		if (typeof ret != 'undefined') return ret;

		return _;
	};

})();