$(document).ready(function() {
  // HEADER
  var $header = $('.header-container');
  var $nav = $('#portal-globalnav');
  var $navItems = $nav.children('li');

  $header.css('visibility', 'visible');
  $('.plone-navbar').css({
    'visibility': 'visible',
    'position': 'inherit'
  });

  // Align submenu to the right if overflows the main navigation menu
  var mainMenuWidth = $header.width();
  $navItems.mouseenter(function() {
    var $this = $(this);
    var $submenu = $this.children('.submenu');
    var subMenuWidth = $submenu.width();

    if ($submenu.length > 0) {
      var subMenuLeftPos = $submenu.offset().left;
      if (mainMenuWidth - (subMenuWidth + subMenuLeftPos) < 0) {
        $submenu.css({
          'right': 0,
          'left': 'auto'
        });
      }
    }

  });


  // Insert icon for external links inside the <a> tag
  // in the navigation menu
  $('#portal-globalnav a').each(function() {
    var $this = $(this);
    var $icon = $('<i class="glyphicon external-icon link-https"/>');
    var a = new RegExp('/' + window.location.host + '/');
    if ($this.parents('.submenu').length) {
      if (!a.test(this.href)) {
        $this.append($icon);
      }
    } else {
      if (!a.test(this.href)) {
        $this.prepend($icon);
      }
    }
  });


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
      totalNavItemsWidth += $li.outerWidth(true);
    });
    $('.navbar-nav').attr('data-width', totalNavItemsWidth + 10);
    clone.remove();
  }

  function collapseHeader() {
    var $header = $('.header-container');
    var headerWidth = $header.width();
    var logoWidth = $('.header-logo').outerWidth(true);
    var rightActionsWidth = $('.right-actions').outerWidth(true) + 35;
    var menuWidth = $('.navbar-nav').data('width');

    var availableSpace = headerWidth - (logoWidth + menuWidth);
    var shouldCollapseHeader = availableSpace <= rightActionsWidth;
    $header.toggleClass('collapse-header', shouldCollapseHeader);

    if ($header.hasClass('collapse-header')) {
      var navAvailableSpace;
      if ($(window).width() >= 480) {
        navAvailableSpace = headerWidth - logoWidth;
      } else {
        navAvailableSpace = headerWidth;
      }
      var collapseNav = menuWidth >= navAvailableSpace;
      $header.toggleClass('collapse-nav', collapseNav);
    } else {
      $header.removeClass('collapse-nav');
    }
  }

  // move Eionet logo text in the collapsed menu
  // when it's running out of space in the header
  function moveLogoText() {
    var $logoText = $('.logo-text');
    if ($(window).width() <= 480) {
      $logoText.prependTo('.plone-navbar-collapse');
    } else {
      $logoText.appendTo('.header-logo a');
    }
  }

  // sticky header on mobile devices
  var headerPos = $header.offset().top + 35;
  var lastScrollTop = 0;
  var $toolbar = $('.plone-toolbar-logo');

  if ($(window).width() <= 767) {
    $(window).scroll(function() {
      var currentScroll = $(window).scrollTop();
      if (currentScroll >= headerPos) {
        $header.addClass('sticky-header');
        $toolbar.css('top', '10px');
      } else {
        $header.removeClass('sticky-header');
        $toolbar.css('top', '46px');
      }
    });
  }

  // Portlet navigation tree
  $('.portletNavigationTree li').each(function() {
    var $li = $(this);
    if ($li.children('.navTree').length > 0) {
      $li.addClass('has-subitem');
     }
  });


  // Breadcrumb home section
  var $bh = $('#breadcrumbs-home a');
  // $bh.text('Eionet');
  $bh.prepend('<i class="glyphicon glyphicon-home"/>');

  $('table').wrap('<div class="table-wrapper"></div>');

  // collapse header
  var isMobile = $(window).width() <= 767;
  var isSmallScreen = $(window).width() <= 1280;
  $header.toggleClass('collapse-header', isSmallScreen);
  $header.toggleClass('collapse-header collapse-nav', isMobile);

  getNavItemsTotalWidth();
  moveLogoText();
  collapseHeader();

  var resizeTimer;
  $(window).on('resize',function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 100);
  });

  function doneResizing() {
    getNavItemsTotalWidth();
    moveLogoText();
    collapseHeader();
  }
});
