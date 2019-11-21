/* global Urls:readable */
// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

import $ from 'jquery'

// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import './css/styles.css';

/**
 * request server-end rendered paradigm and plunk it in place
 *
 * @param lemmaID {number} the id of the lemma in database
 */
function loadParadigm(lemmaID) {
  let xhttp = new XMLHttpRequest();

  xhttp.onloadstart = function () {
    // Show the loading indicator:
    indicateLoading()
  };

  xhttp.onload = function () {
    if (xhttp.status === 200) {
      window.history.pushState('', document.title, Urls['cree-dictionary-index-with-lemma'](lemmaID));
      hideInstruction();
      emptySearchResultList();
      $('main').append(xhttp.responseText);

      indicateLoadedSuccessfully()
    } else {
      indicateLoadingFailure()
    }
  };

  xhttp.onerror = function () {
  };

  xhttp.open('GET', Urls['cree-dictionary-lemma-detail'](lemmaID), true);
  xhttp.send()
}

const ERROR_CLASS = 'search-progress--error';
const LOADING_CLASS = 'search-progress--loading';

/**
 * Make a 10% progress bar. We actually don't know how much there is left,
 * but make it seem like it's thinking about it!
 */
function indicateLoading() {
  let progress = document.getElementById('loading-indicator');
  progress.max = 100;
  progress.value = 10;
  progress.classList.remove(ERROR_CLASS);
  progress.classList.add(LOADING_CLASS)
}


function indicateLoadedSuccessfully() {
  let progress = document.getElementById('loading-indicator');
  progress.value = 100;
  hideLoadingIndicator()
}

function indicateLoadingFailure() {
  // makes the loading state "indeterminate", like it's loading forever.
  let progress = document.getElementById('loading-indicator');
  progress.removeAttribute('value');
  progress.classList.add(ERROR_CLASS)
}

function hideLoadingIndicator() {
  let progress = document.getElementById('loading-indicator');
  progress.classList.remove(LOADING_CLASS, ERROR_CLASS)
}

/**
 * clean search results (boxed shaped entries)
 */
function emptySearchResultList() {
  $('#search-result-list').html('')
}

/**
 * clean paradigm details
 */
function cleanParadigm() {
  $('#paradigm').remove()
}


function showInstruction() {
  let instruction = $('#introduction-text');
  instruction.show()
}

function hideInstruction() {
  let instruction = $('#introduction-text');
  instruction.hide()
}

/**
 * use xhttp to load search results in place
 *
 * @param {jQuery} $input
 */
function loadResults($input) {
  let text = $input.val();
  let $searchResultList = $('#search-result-list');

  if (text !== '') {
    issueSearch()
  } else {
    goToHomePage()
  }

  function issueSearch() {
    window.history.replaceState(text, document.title, Urls['cree-dictionary-index-with-word'](text));

    hideInstruction();

    let xhttp = new XMLHttpRequest();

    xhttp.onloadstart = function () {
      // Show the loading indicator:
      indicateLoading()
    };

    xhttp.onload = function () {
      if (xhttp.status === 200) {
        // user input may have changed during the request
        const inputNow = $input.val();
        if (inputNow === text) { // hasn't changed
          // Remove loading cards
          indicateLoadedSuccessfully();
          cleanParadigm();
          $searchResultList.html(xhttp.responseText);
          $searchResultList.find('.definition-title__link').on('click', function () {
            loadParadigm($(this).data('lemma-id'))
          })

        } else { // changed. Do nothing
        }
      } else {
        indicateLoadingFailure()
      }
    };

    xhttp.onerror = function () {
    };
    xhttp.open('GET', Urls['cree-dictionary-search-results'](text), true);
    xhttp.send()
  }

  function goToHomePage() {
    window.history.replaceState(text, document.title, Urls['cree-dictionary-index']());

    showInstruction();

    hideLoadingIndicator();
    $searchResultList.empty()
  }

}

/**
 * Change tab title according to user input in the search bar
 *
 * @param inputVal {string}
 */
function changeTitleByInput(inputVal) {
  setSubtitle(inputVal ? '🔎 ' + inputVal : null);
}

function setSubtitle(subtitle) {
  let defaultTitle = 'itwêwina: the online Cree dictionary';
  document.title = subtitle ? `${subtitle} — ${defaultTitle}` : defaultTitle
}

$(() => {
  // XXX: HACK! reloads the site when the back button is pressed.
  $(window).on('popstate', function () {
    location.reload()
  });

  let route = window.location.pathname;
  let $input = $('#search');

  // Tiny router.
  if (route === '/') {
    // Homepage
    setSubtitle(null)
  } else if (route === '/about') {
    // About page
    setSubtitle('About')
  } else if (route.match(/^[/]lemma[/].+/)) {
    let initialLemmaID = $('#initial-lemma-id').val();
    loadParadigm(parseInt(initialLemmaID))
  } else if (route.match(/^[/]search[/].+/)) {
    loadResults($input)
  } else {
    console.assert('not sure what page this is: ' + route);
  }

  $input.on('input', () => {
    loadResults($input);
    changeTitleByInput($input.val())
  })
});
