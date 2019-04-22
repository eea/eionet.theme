$(document).ready(function() {

  // HEADER
  var $win = $(window);
  var $header = $('.header-container');
  var $nav = $('#portal-globalnav');
  var $navItems = $nav.children('li');

  // Align submenu to the right if overflows the main navigation menu
  var mainMenuWidth = $header.width();
  $navItems.mouseenter(function() {
    var $this = $(this);
    var $submenu = $this.children('.submenu');
    var subMenuWidth = $submenu.width();

    if ($submenu.length > 0) {
      var subMenuLeftPos = $submenu.offset().left;
    }

    if (mainMenuWidth - (subMenuWidth + subMenuLeftPos) < 0) {
      $submenu.css({
        'right': 0,
        'left': 'auto'
      });
    }
  });


  // Insert icon for external links inside the <a> tag
  $('.submenu a').each(function() {
    var $this = $(this);
    var a = new RegExp('/' + window.location.host + '/');
    if (!a.test(this.href)) {
      $this.append('<i class="glyphicon external-icon link-https"/>');
    }
  });


  // Fire resize event after the browser window resizing it's completed
  var resizeTimer;
  $win.on('resize',function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  function alignHeaderContent() {
    var ww = $win.width();
    var cw = $('#main-container').width();
    var $toolbar = $('.plone-toolbar-container');
    // var $cn = $('.plone-navbar-collapse');
    var tw = $toolbar.width();
    var cwRight;
    if ($toolbar.length > 0) {
      cwRight = (ww - cw - tw + 30) / 2;
    } else {
      cwRight = (ww - cw + 30) / 2;
    }

    $header.css('padding', '0 ' + cwRight + 'px');
    // $cn.find('a').css('padding', '1em ' + cwRight + 'px');
    // $cn.find('.submenu a').css('padding', '0.5em ' + cwRight + 'px');
    $('.right-actions').css('right', cwRight);
  }

  // Collapse navigation and move search section
  // when it's running out of space in the header

  function getNavItemsTotalWidth() {
    var clone = $("#portal-globalnav").clone();
    clone.addClass('cloned-menu');
    $('#portal-globalnav-wrapper').append(clone);
    var totalNavItemsWidth = 0;
    var $clonedNavItems = $('.cloned-menu').children('li');
    $clonedNavItems.each(function() {
      var $li = $(this);
      totalNavItemsWidth += $li.outerWidth(true) + 4;
    });
    $('.navbar-nav').attr('data-width', totalNavItemsWidth);
    clone.remove();
  }

  function collapseHeader() {
    var headerWidth = $header.width();
    var logoWidth = $('.header-logo').outerWidth(true);
    var rightActionsWidth = $('.right-actions').width();
    var menuWidth = $('.navbar-nav').data('width');

    var availableSpace = headerWidth - logoWidth - menuWidth;

    var isMobile = $win.width() <= 767;
    $header.toggleClass('collapse-header collapse-nav', isMobile);

    var collapseHeader = availableSpace <= rightActionsWidth;
    $header.toggleClass('collapse-header', collapseHeader);

    if ($header.hasClass('collapse-header')) {
      var navAvailableSpace = headerWidth - logoWidth;
      var collapseNav = menuWidth >= navAvailableSpace;
      $header.toggleClass('collapse-nav', collapseNav);
    }
  }

  // move Eionet logo text in the collapsed menu
  // when it's running out of space in the header
  function moveLogoText() {
    var $logoText = $('.logo-text');
    if ($win.width() <= 480) {
      $logoText.prependTo('.plone-navbar-collapse');
    } else {
      $logoText.appendTo('.header-logo a');
    }
  }

  // sticky header on mobile devices
  var headerPos = $header.offset().top + 35;
  var $toolbar = $('.plone-toolbar-logo');

  if ($win.width() <= 767) {
    $win.scroll(function() {
      var currentScroll = $win.scrollTop();
      if (currentScroll >= headerPos) {
        $header.addClass('sticky-header');
        $toolbar.css('top', '10px');
      } else {
        $header.removeClass('sticky-header');
        $toolbar.css('top', '46px');
      }
    });
  }

  // Breadcrumb home section
  var $bh = $('#breadcrumbs-home a');
  $bh.text('Eionet');
  $bh.prepend('<i class="glyphicon glyphicon-home"/>');

  $(window).load(function() {
    alignHeaderContent();
    getNavItemsTotalWidth();
    collapseHeader();
    moveLogoText();
  });

  function doneResizing() {
    alignHeaderContent();
    collapseHeader();
    moveLogoText();
  }
});
