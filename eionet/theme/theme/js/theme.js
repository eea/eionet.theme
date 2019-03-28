$(document).ready(function() {
  // GLOBAL MENU:
  // Align submenu to the right if overflows the main navigation menu
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

  // insert icon for external links inside the <a> tag
  var submenuItem = $('#portal-globalnav').find('.submenu li a');
  submenuItem.each(function() {
    var $ext = $('<i class="glyphicon external-icon link-https"/>');
    if (!(location.hostname === this.hostname || !this.hostname.length)) {
      $ext.appendTo($(this));
    }
  });

  var $win = $(window);
  var $sfw = $('.header-container');
  var headerPos = $sfw.offset().top;
  var $toolbar = $('.plone-toolbar-logo');
  var resizeTimer;

  // fire resize event after the browser window resizing it's completed
  $win.resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  function doneResizing() {
    var windowsize = $win.width();
    if (windowsize <= 480) {
      $('.logo-text').prependTo('.plone-navbar-collapse');
    }
  }

  // sticky header on mobile devices
  if ($win.width() <= 767) {
    $win.scroll(function() {
      var currentScroll = $win .scrollTop();
      if (currentScroll >= headerPos) {
        $sfw.addClass('sticky-header');
        $toolbar.css('top', '10px');
      } else {
        $sfw.removeClass('sticky-header');
        $toolbar.css('top', '46px');
      }
    });
  }


  // Breadcrumb home section
  var $bh = $('#breadcrumbs-home a');
  $bh.text('Eionet');
  $bh.prepend('<i class="glyphicon glyphicon-home"/>');

});
