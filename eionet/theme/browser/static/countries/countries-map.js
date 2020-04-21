var _selectedMapSection = null;
var _mapTooltip = null;
var countrySettings = [];   // country list extracted from ajax json
var _world = {};

var focusCountryNames = [   // Member countries
  "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
  "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
  "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania",
  "Luxembourg", "Malta", "Netherlands", "Norway", "Poland", "Portugal",
  "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
  "Turkey"
];
var coopCountries = [
  "Albania", "Bosnia and Herzegovina", "Kosovo*", "North Macedonia",
  "Montenegro", "Serbia"
];

var allCountries = coopCountries + focusCountryNames;


function filterCountriesByNames(countries, filterIds) {
  var features = {
    type: 'FeatureCollection',
    features: []
  };
  countries.forEach(function (c) {
    if (filterIds.indexOf(c.properties.SHRT_ENGL) === -1) {
      return;
    }
    features.features.push(c);
  });
  return features;
}


function drawCountries(world) {
  var svg = d3
    .select("body")
    .select(".svg-map-container svg")
    ;
  svg.selectAll("*").remove();

  var focusCountriesFeature = filterCountriesByNames(world, allCountries);

  var width = Math.round($(svg.node()).width());
  var height = Math.round($(svg.node()).height());

  var opts = {
    'world': world,
    'svg': svg,
    'coordinates': {
      'x': 0,
      'y': 0,
      'width': width,
      'height': height
    },
    'focusCountries': {
      'names': allCountries,
      'feature': focusCountriesFeature
    },
    'zoom': 0.95
  };

  renderCountriesBox(opts);

  var mo = {
    'svg': svg,
    'world': world,
    'viewport': [width, height],
    'countries': ['Malta', 'Liechtenstein', 'Luxembourg'],
    'start': [width - 60, 10],
    'side': 'left'
    // 'size': 80,
    // 'space': 6,
  };
  drawMaplets(mo);

}

function initmap(world) {
  function drawMap(width) {
    drawCountries(world);
  }

  // fire resize event after the browser window resizing it's completed
  var resizeTimer;
  $(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doneResizing, 500);
  });

  var width = $('.svg-map-container svg').width();
  function doneResizing() {
    drawMap(width);
  }
  drawMap(width);

  $('.map-loader').fadeOut(600);
}

function listCountryLinks(world) {
  var focusCountriesFeature = filterCountriesByNames(world, allCountries);

  var opts = {
    'world': world,
    'focusCountries': {
      'names': allCountries,
      'feature': focusCountriesFeature
    }
  };

  var countries = opts.focusCountries;
  var opts_world = opts.world;

  opts_world.forEach(function (country) {
    var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
    if (available) {
      renderCountryList(country);
    }
  });

  // sort countries list alphabetically
  var $cl = $('.map-right-section');
  $cl.hide();
  $('.countries-list').each(function() {
    var $ul = $(this);
    $ul.append($ul.children('li').get().sort(function(a, b) {
      var aText = $(a).text(), bText = $(b).text();
      return aText < bText ? -1 : aText > bText ? 1 : 0;
    }));
  });
  $cl.fadeIn('slow');
}

$(document).ready(function() {
  // initialize the countries map
  var cpath = '++plone++eionet.theme/countries/euro-countries-simplified.geojson';
  var fpath = '++plone++eionet.theme/countries/countries.tsv';

  var $sw = $('.svg-map-container');
  var $load = $('<div class="map-loader">' +
    '<div class="loading-spinner"></div>' +
    '<span class="loading-text">Loading map ...</span></div>');
  $sw.append($load);

  d3.json(cpath, function (world) {
    d3.tsv(fpath, function (flags) {
      window._world = world;
      window._flags = flags;
      initmap(window._world.features);
      listCountryLinks(window._world.features);
    });
  });
});

function renderGraticule(container, klass, steps, pathTransformer) {
  container     // draw primary graticule lines
    .append('g')
    .attr('class', klass)
    .selectAll('path')
    .data(d3.geoGraticule().step(steps).lines())
    .enter()
    .append('path')
    .attr('d', pathTransformer)
    ;
}

function getCountryClass(country, countries) {
  var k = 'country-outline';
  var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;
  if (available) {
      k += ' country-available';
  }

  var name = country.properties.SHRT_ENGL;
  if (coopCountries.indexOf(name) > -1) {
    k += ' country-green';
  }

  return k;
}

function showCountryPopup(country) {
  var $container = $('.svg-map-container').append($("<div>"));
  var $modal = $container.patPloneModal({
    position: 'center middle',
    width: '60%',
    title: country.properties.SHRT_ENGL,
    backdropOptions: {
      closeOnEsc: false,
      closeOnClick: false,
      opacity: '0'
    }
  });
  var modal = $modal.data('pattern-plone-modal');
  modal.show();
  var cId = country.properties.CNTR_ID;
  var cName = country.properties.SHRT_ENGL;
  var cooptype = coopCountries.indexOf(cName) > -1 ? 'cc' : 'mc';
  var ctext = countryTpl
    .replace(/ccode/g, cId.toLowerCase())
    .replace(/CountryName/g, cName)
    .replace(/ctype/g, cooptype)
  ;

  modal.$modal.find('.plone-modal-title').empty().append(cName);
  modal.$modal.find('.plone-modal-body').empty().append(ctext);
  modal.$modal.find('a.link-webpage').each(function() {
    var $a = $(this);
    var url = new RegExp('/' + window.location.host + '/');
    $a.click(function() {
      if (!url.test(this.href)) {
        window.open($a.attr('href'));
      } else {
        window.location = $a.attr('href');
      }
    });
  });

  return false;
}


// tooltip with country names on hover
var countryNameTooltip = d3.select("body")
    .append("div")
    .attr('class', 'tooltip')
    ;


function getIEVersion() {
  var sAgent = window.navigator.userAgent;
  var Idx = sAgent.indexOf("MSIE");

  // If IE, return version number.
  if (Idx > 0){
    return parseInt(sAgent.substring(Idx+ 5, sAgent.indexOf(".", Idx)), 10);
  }

  // If IE 11 then look for Updated user agent string.
  else if (!!navigator.userAgent.match(/Trident\/7\./)){
    return 11;
  }

  else {
    return 0; //It is not IE
  }
}


function renderCountryFlag(parent, country, bbox, cpId) {
  var flag = parent
    .append('image')
    .attr('class', 'country-flag')
    .attr('href', function() {
      if (getIEVersion() > 0) {
        // TODO: get the fallback svg?
        return '++theme++climateadaptv2/static/images/fallback.svg';
      } else {
        return country.url;
      }
    })
    .attr("preserveAspectRatio", "none")
    .attr('opacity', '0')
    .attr('clip-path', 'url(#' + cpId + ')')
    .attr('x', bbox.x)
    .attr('y', bbox.y)
    .attr('height', bbox.height)
    .attr('width', bbox.width)
    .on('click', function (e) {
      showCountryPopup(country);
    })
    .on('mouseover', function() {
      var countryName = country.properties.SHRT_ENGL.toUpperCase();
      d3.select(this).attr('opacity', 1);
      return countryNameTooltip
      .style("display", "block")
      .html(countryName);
    })
    .on('mousemove', function() {
      var countryName = country.properties.SHRT_ENGL.toUpperCase();
      return countryNameTooltip
      .style("display", "block")
      .style("top", (d3.event.pageY) + "px")
      .style("left", (d3.event.pageX + 10) + "px")
      .html(countryName);
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 0);
      return countryNameTooltip
      .style("display", "none");
    })
    ;
  return flag;
}


function makeid() {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

  for (var i = 0; i < 5; i++){
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }

  return text;
}


function renderCountry(map, country, path, countries, x, y) {

  var cprectid = makeid();    // unique id for this map drawing
  var klass = getCountryClass(country, countries);
  var cId = 'c-' + cprectid + '-' + country.properties.id;
  var cpId = 'cp-' + cprectid + '-' + country.properties.id;

  var available = countries.names.indexOf(country.properties.SHRT_ENGL) !== -1;

  var parent = map
    .append('g')
    .attr('class', klass)
    ;

  parent       // define clipping path for this country
    .append('defs')
    .append('clipPath')
    .attr('id', cpId)
    .append('path')
    .attr('d', path(country))
    .attr('x', x)
    .attr('y', y)
    ;

  var outline = parent       // this is the country fill and outline
    .append('path')
    .attr('id', cId)
    .attr('x', x)
    .attr('y', y)
    .attr('d', path(country))
    ;

  if (available) {
    var bbox = outline.node().getBBox();
    renderCountryFlag(parent, country, bbox, cpId);
    // renderCountryLabel(country, path);
  }
}


function passThruEvents(g) {

  function passThru(d) {
    // console.log('passing through');
    var e = d3.event;

    var prev = this.style.pointerEvents;
    this.style.pointerEvents = 'none';

    var el = document.elementFromPoint(d3.event.x, d3.event.y);

    var e2 = document.createEvent('MouseEvent');
    e2.initMouseEvent(
      e.type,
      e.bubbles,
      e.cancelable,
      e.view,
      e.detail,
      e.screenX,
      e.screenY,
      e.clientX,
      e.clientY,
      e.ctrlKey,
      e.altKey,
      e.shiftKey,
      e.metaKey,
      e.button,
      e.relatedTarget
    );

    el.dispatchEvent(e2);

    this.style.pointerEvents = prev;
  }

  g
    // .on('mousemove.passThru', passThru)
    .on('mouseover', passThru)
  // .on('mousedown.passThru', passThru)
  ;

}


function renderCountryLabel(country, path, force) {
  var parent = d3.select('.svg-map-container svg');
  var klass = force ? 'country-label maplet-label' : 'country-label';
  var g = parent
    .append('g')
    .attr('class', klass)
    ;
  if (
    // these are very small countries that we will create a maplet for;
    (
      country.properties.SHRT_ENGL === 'Liechtenstein' ||
      country.properties.SHRT_ENGL === 'Luxembourg' ||
      country.properties.SHRT_ENGL === 'Malta'
    ) && !force) {
      return;
    }

  var delta = force ? 20 : 0;

  var pId = 'pl-' + country.id;
  var center = path.centroid(country);

  var label = g
    .append('text')
    // .attr('class', 'place-label')
    .attr('id', pId)
    .attr('x', center[0])
    .attr('y', center[1] + delta)
    .attr('text-anchor', 'middle')
    .text(country.properties.SHRT_ENGL.toUpperCase())
    ;

  var bbox = label.node().getBBox();

  g
    .append('rect')
    // .attr('class', 'place-label-bg')
    .attr('x', bbox.x - 1)
    .attr('y', bbox.y - 1)
    .attr('width', bbox.width + 2)
    .attr('height', bbox.height + 2)
    ;

  label.raise();
  passThruEvents(g);
}

function renderCountryList(country) {
  var mc = d3.select('.member-countries');
  var cc = d3.select('.cooperating-countries');
  var name = country.properties.SHRT_ENGL;

  if (focusCountryNames.indexOf(name) > -1) {
    var mc_list = mc
    .append('li')
    .insert('a')
    .text(name)
    .attr('class', 'c-blue')
    .on('click', function() {
      showCountryPopup(country);
    })
    ;
  }

  if (coopCountries.indexOf(name) > -1) {
    var cc_list = cc
    .append('li')
    .insert('a')
    .text(name)
    .attr('class', 'c-green')
    .on('click', function() {
      showCountryPopup(country);
    })
    ;
  }
}

var countryTpl = '' +
'<ul class="urllist">' +
'  <li>' +
'    <i class="glyphicon link-external"></i>' +
'    <a class="link-webpage" href="http://cdr.eionet.europa.eu/ccode">' +
'      CDR Data Deliveries</a>' +
'    List of files uploaded to the Central Data Repository (CDR)</li>' +
'' +
'  <li>' +
'    <a class="link-webpage" href="/ldap-organisations?country=ccode">' +
'      Eionet Organisations</a>' +
'    List of organisations registered in the Eionet Directory</li>' +
'' +
'  <li>' +
'    <a class="link-webpage" href="/ldap-roles/?role_id=eionet-nfp-ctype-ccode">NFP CountryName address</a></li>' +
'' +
'  <li>' +
'    <a class="link-webpage" href="/ldap-roles/filter?pattern=eionet-nrc-*-ctype-ccode">PCPs and NRCs</a>' +
'    List of all Primary Contact Points and National Reference Centres</li>' +
'' +
'<li>' +
'    <a class="link-webpage" href="/ldap-roles/filter?pattern=reportnet-*-*-ccode">List of Reportnet users</a></li>' +
'' +
' <li>' +
'    <a class="link-webpage" href="/ldap-roles/filter?pattern=extranet-*-*-ccode">List of Extranet users</a></li>' +
'</ul>';


function setCountryFlags(countries, flags) {
  // annotates each country with its own flag property
  countries.forEach(function (c) {
    var name = c.properties.SHRT_ENGL;
    if (!name) {
      // console.log('No flag for', c.properties);
      return;
    }
    if (name == 'Czechia'){
        name = 'Czech';
    }
    if (name == 'Kosovo*'){
        name = 'Kosovo';
    }
    var cname = name.replace(' ', '_');
    if (cname == 'Bosnia_and Herzegovina'){
        cname = 'Bosnia_and_Herzegovina';
    }
    flags.forEach(function (f) {
      if (f.url.indexOf(cname) > -1) {
        c.url = f.url;
      }
    });
  });
}


function renderCountriesBox(opts) {
  var coords = opts.coordinates;
  var countries = opts.focusCountries;

  var svg = opts.svg;
  var world = opts.world;
  var zoom = opts.zoom;
  var cprectid = makeid();    // unique id for this map drawing

  var globalMapProjection = d3.geoAzimuthalEqualArea();

  globalMapProjection
    .scale(1)
    .translate([0, 0])
    ;

  // the path transformer
  var path = d3.geoPath().projection(globalMapProjection);

  var x = coords.x;
  var y = coords.y;
  var width = coords.width;
  var height = coords.height;
  // var extent = [[x + 20, y + 20], [x + coords.width - 20 , y + coords.height - 20]];
  // globalMapProjection.fitExtent(extent, countries.feature);

  var b = path.bounds(countries.feature);
  var cwRatio = (b[1][0] - b[0][0]) / width;    // bounds to width ratio
  var chRatio = (b[1][1] - b[0][1]) / height;   // bounds to height ratio
  var s = zoom / Math.max(cwRatio, chRatio);
  var t = [
    (width - s * (b[1][0] + b[0][0])) / 2 + x,
    (height - s * (b[0][1] + b[1][1])) / 2 + y
  ];

  globalMapProjection.scale(s).translate(t);

  svg
    .append('defs')    // rectangular clipping path for the whole drawn map
    .append('clipPath')
    .attr('id', cprectid)
    .append('rect')
    .attr('x', x)
    .attr('y', y)
    .attr('height', height)
    .attr('width', width)
    ;

  var map = svg   // the map will be drawn in this group
    .append('g')
    .attr('clip-path', 'url(#' + cprectid + ')')
    ;

  map     // the world sphere, acts as ocean
    .append("path")
    .datum({type: "Sphere"})
    .attr("class", "sphere")
    .attr("d", path)
    ;

  renderGraticule(map, 'graticule', [20, 10], path);
  renderGraticule(map, 'semi-graticule', [5, 5], path);

  setCountryFlags(countries.feature.features, window._flags);

  world.forEach(function (country) {
    renderCountry(map, country, path, countries, x, y);
  });

  return path;
}

function drawMaplet(opts) {
  var msp = opts.coordinates;
  var svg = opts.svg;
  svg
    .append('rect')
    .attr('class', 'maplet-outline')
    .attr('x', msp.x)
    .attr('y', msp.y)
    .attr('width', msp.width)
    .attr('height', msp.height)
    ;

  var path = renderCountriesBox(opts);
  renderCountryLabel(opts.focusCountries.feature.features[0], path, true);
}


function getMapletStartingPoint(
  viewport,   // an array of two integers, width and height
  startPoint, // an array of two numbers, x, y for position in viewport
  index,      // integer, position in layout
  side,       // one of ['top', 'bottom', 'left', right']
  spacer,     // integer with amount of space to leave between Maplets
  boxDim,      // array of two numbers, box width and box height
  titleHeight // height of title box
) {

  // return value is array of x,y
  // x: horizontal coordinate
  // y: vertical coordinate

  var bws = boxDim[0] + spacer;   // box width including space to the right
  var bhs = boxDim[1] + spacer + titleHeight;

  var mutator = travelToOppositeMutator(startPoint, viewport, [bws, bhs]);

  var mutPoint = [startPoint[0], startPoint[1]];

  for (var i = 0; i < index; i++) {
    mutPoint = mutator(mutPoint, index);
  }

  // TODO: this could be improved, there are many edge cases
  switch (side) {
    case 'top':
      mutPoint[1] = startPoint[1];
      break;
    case 'bottom':
      mutPoint[1] = startPoint[1] - bhs;
      break;
    case 'left':
      mutPoint[0] = startPoint[0];
      break;
    case 'right':
      mutPoint[0] = startPoint[0] - bws;
      break;
  }

  return {
    x: mutPoint[0],
    y: mutPoint[1]
  };
}


function drawMaplets(opts) {
  var svg = opts.svg;
  var world = opts.world;
  var viewport = opts.viewport;
  var start = opts.start;
  var side = opts.side;

  var g = svg   // the map will be drawn in this group
    .append('g')
    .attr('class', 'maplet-container')
    ;

  var countries = opts.countries;

  countries.forEach(function (name, index) {
    var feature = filterCountriesByNames(world, [name]);
    var boxw = 50;
    var boxh = 50;
    var space = 10;

    var msp = getMapletStartingPoint(
      viewport,
      start,
      index,
      side,
      space,
      [boxw, boxh],
      0
    );

    var zo = {
      'world': world,
      'svg': g,
      'coordinates': {
        'x': msp.x,
        'y': msp.y,
        'width': boxw,
        'height': boxh
      },
      'focusCountries': {
        'names': [name],
        'feature': feature
      },
      'zoom': 0.5
    };
    drawMaplet(zo);
  });
}


function createTooltip(opts) {
  var x = opts.coords[0];
  var y = opts.coords[1];
  var content = opts.content[_selectedMapSection];
  var name = opts.name;
  var url = opts.url;

  $('#map-tooltip').remove();
  var style = 'top:' + x + 'px; left: ' + y + 'px';
  var content_div = $('<div>')
    .attr('id', 'tooltip-content')
    .append(content)
    ;
  var h3_name = $('<h3>')
    .append(name)
    ;
  var link_tag = $('<a>')
    .attr('href', url)
    .append(h3_name)
    ;
  var name_div = $('<div>')
    .attr('id', 'country-name')
    .append(link_tag)
    ;
  var tooltip = $("<div id='map-tooltip'>")
    .attr('style', style)
    .append(name_div)
    .append(content_div)
    ;
  $('body').append(tooltip);
}


function travelToOppositeMutator(start, viewport, delta) {
  // point: the point we want to mutate
  // start: starting point (the initial anchor point)
  // viewport: array of width, height
  // delta: array of dimensions to travel

  var center = [viewport[0] / 2, viewport[1] / 2];

  var dirx = start[0] > center[0] ? -1 : 1;
  var diry = start[1] > center[1] ? -1 : 1;

  return function (point) {
    var res = [
      point[0] + delta[0] * dirx,
      point[1] + delta[1] * diry
    ];
    return res;
  };
}
