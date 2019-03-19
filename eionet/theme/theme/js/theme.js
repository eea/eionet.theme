$(document).ready(function() {
  // Navigation menu: align submenu to the right
  // if overflows the main navigation menu
  var mainMenuWidth = $('.header-container').width();

  $('#portal-globalnav li').mouseenter(function() {
    var $this = $(this);
    var subMenuWidth = $this.find('.submenu').width();

    if ($this.find('.submenu').length > 0) {
      var subMenuLeft = $this.children('.submenu').offset().left;
    }

    if (mainMenuWidth - (subMenuWidth + subMenuLeft) < 0) {
      $this.children('.submenu').css({
        'right': 0,
        'left': 'auto'
      });
    }
  });

  // sticky header on mobile devices
  var $sfw = $('.header-container');
  var headerPos = $sfw.offset().top;
  var $win = $(window);

  if ($win.width() <= 767) {
    $win.scroll(function() {
      var currentScroll = $(window).scrollTop();

      if (currentScroll >= headerPos) {
        $sfw.addClass('sticky-header');
        $('.plone-toolbar-logo').css('top', '14px');
      } else {
        $sfw.removeClass('sticky-header');
        $('.plone-toolbar-logo').css('top', '50px');
      }
    });
  }

});
